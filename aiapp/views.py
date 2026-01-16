from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from backend.aipipeline import runbatch_pipeline
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from io import BytesIO
from django.shortcuts import render
from .models import GeminiGenerationStats
import os
import zipfile
from django.http import HttpResponse
from django.conf import settings
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
def generate_page(request):
    return render(request, "generate.html")


class FashionGenerateAPI(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        gender = request.data.get("gender")
        bodytype = request.data.get("bodytype")
        pattern = request.FILES.get("pattern")
        files = request.FILES.getlist("designs")
        generated_dir = os.path.join(settings.MEDIA_ROOT, "generated")

        if os.path.exists(generated_dir):
            for filename in os.listdir(generated_dir):
                file_path = os.path.join(generated_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print("Error deleting file:", file_path, e)

        print("---- Received Request ----")
        print(f"Gender: {gender}, Bodytype: {bodytype}")

        print(f"Received {len(files)} design files")
        print(f"Received pattern file: {pattern.name if pattern else 'None'}")

        if not files:
            return Response({"error": "No design images uploaded"}, status=400)

        if len(files) > 5:
            return Response({"error": "Maximum 5 design images allowed"}, status=400)

        # Always use batch pipeline (it handles single & multiple)
        results = runbatch_pipeline(files, gender, bodytype, pattern)

        output_urls = []

        for item in results:
            image = item["output"]
            if isinstance(image, str):
                print("Skipping failed image:", image)
                continue

            filename = f"{item['file_name'].split('.')[0]}_{item['view'].replace(' ', '_')}.png"
            filepath = os.path.join("generated", filename)

            # Convert PIL image to Django file
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            buffer.seek(0)

            saved_path = default_storage.save(filepath, ContentFile(buffer.read()))

            output_urls.append({
                "file": item["file_name"],
                "view": item["view"],
                "url": default_storage.url(saved_path)
            })
        # counter, created = GeminiGenerationStats.objects.get_or_create(id=1)

        # new_images = len(output_urls)

        # # Add to total images
        # counter.total_images += new_images
        # COST_PER_IMAGE = 0.04

        # # Calculate cost
        # counter.total_cost = counter.total_images * COST_PER_IMAGE

        # counter.save()

        return Response({
            "status": "success",
            "count": len(output_urls),
            "results": output_urls,
            # "cost_per_image": COST_PER_IMAGE,
            # "total_cost": float(counter.total_cost),
        })
    


class DownloadGeneratedImagesAPI(APIView):

    def get(self, request):
        generated_dir = os.path.join(settings.MEDIA_ROOT, "generated")

        if not os.path.exists(generated_dir):
            return HttpResponse("No images found", status=404)

        # Create zip in memory
        zip_buffer = BytesIO()
        zip_file = zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED)

        image_count = 0

        for filename in os.listdir(generated_dir):
            file_path = os.path.join(generated_dir, filename)

            if os.path.isfile(file_path):
                zip_file.write(file_path, arcname=filename)
                image_count += 1

        zip_file.close()

        if image_count == 0:
            return HttpResponse("No images found", status=404)

        # Prepare response
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="generated_images.zip"'

        return response
