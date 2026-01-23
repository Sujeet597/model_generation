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
import json
from datetime import datetime
from datetime import datetime, date
import shutil
from concurrent.futures import ThreadPoolExecutor
import time
ImageFile.LOAD_TRUNCATED_IMAGES = True


##### ----------------------START render page CBF -------------------------------####

def generate_page(request):
    return render(request, "generate.html")

def history_page(request):
    return render(request, "history.html")

##### ----------------------END render page CBF -------------------------------####

### -------------------------START DRF API view ------------------------------#####

class DownloadGeneratedImagesAPI(APIView):

    def get(self, request):
        date_folder = request.GET.get("date")   # e.g. 2026-01-19
        hit_folder = request.GET.get("hit")     # e.g. 2

        if not date_folder or not hit_folder:
            return HttpResponse("date and hit parameters are required", status=400)

        base_dir = os.path.join(settings.MEDIA_ROOT, "generated")
        target_folder = os.path.join(base_dir, date_folder, hit_folder)

        if not os.path.exists(target_folder):
            return HttpResponse("Folder not found", status=404)

        # Create zip in memory
        zip_buffer = BytesIO()
        zip_file = zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED)

        image_count = 0

        for filename in os.listdir(target_folder):
            file_path = os.path.join(target_folder, filename)

            if os.path.isfile(file_path):
                zip_file.write(file_path, arcname=filename)
                image_count += 1

        zip_file.close()

        if image_count == 0:
            return HttpResponse("No images found", status=404)

        # Prepare response
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type="application/zip")
        response["Content-Disposition"] = (
            f'attachment; filename="generated_{date_folder}_{hit_folder}.zip"'
        )

        return response



class GenerationHistoryAPI(APIView):

    def get(self, request):
        json_dir = os.path.join(settings.MEDIA_ROOT, "json")
        stats_file = os.path.join(json_dir, "stats.json")

        if not os.path.exists(stats_file):
            return Response({
                "status": "success",
                "total_images": 0,
                "total_cost": 0,
                "history": []
            })

        with open(stats_file, "r") as f:
            stats = json.load(f)

        return Response({
            "status": "success",
            "total_images": stats.get("total_images", 0),
            "total_cost": stats.get("total_cost", 0),
            "history": stats.get("history", [])
        })
    

class FashionGenerateAPI(APIView):

    def post(self, request):
        gender = request.data.get("gender")
        bodytype = request.data.get("bodytype")
        pattern = request.FILES.get("pattern")
        files = request.FILES.getlist("designs")
        model = request.FILES.getlist("model")
        images_count = request.data.get("imagesCount", 1)
        print("Received imagesCount:", images_count)

        today_str = date.today().strftime("%Y-%m-%d")
        generated_dir = os.path.join(settings.MEDIA_ROOT, "generated", today_str)
        generated_root = os.path.join(settings.MEDIA_ROOT, "generated")
        os.makedirs(generated_dir, exist_ok=True)
        

        # Delete old folders
        if os.path.exists(generated_root):
            for folder in os.listdir(generated_root):
                folder_path = os.path.join(generated_root, folder)

                # If it's a folder and not today → delete it
                if folder != today_str and os.path.isdir(folder_path):
                    try:
                        shutil.rmtree(folder_path)
                        print("Deleted old folder:", folder_path)
                    except Exception as e:
                        print("Error deleting folder:", folder_path, e)

        existing_folders = [
            f for f in os.listdir(generated_dir)
            if os.path.isdir(os.path.join(generated_dir, f)) and f.isdigit()
        ]
        next_index = str(len(existing_folders) + 1)
        hit_folder = os.path.join(generated_dir, next_index)
        os.makedirs(hit_folder, exist_ok=True)

        json_dir = os.path.join(settings.MEDIA_ROOT, "json")

        
        os.makedirs(json_dir, exist_ok=True)
        ai_start = time.time()
        print("ai_start", ai_start)

        # Run AI in background thread
        with ThreadPoolExecutor() as executor:
            results = executor.submit(
                runbatch_pipeline, files, gender, bodytype, model, images_count, pattern
            ).result()
        ai_time = round(time.time() - ai_start, 2)

        # -----------------------------
        # ⏱️ IMAGE SAVING TIME
        # -----------------------------
        save_start = time.time()
        print("take_time", save_start - ai_start)

        output_urls = []
        generated_names = []
        uploaded_names = [f.name for f in files]

        for item in results:
            image = item["output"]
            if isinstance(image, str):
                continue

            filename = f"{item['file_name'].split('.')[0]}_{item['view'].replace(' ', '_')}.png"
            filepath = os.path.join("generated", today_str, next_index, filename)

            buffer = BytesIO()
            image.save(buffer, format="PNG")
            buffer.seek(0)

            default_storage.save(filepath, ContentFile(buffer.read()))
            generated_names.append(filename)

            output_urls.append({
                "file": item["file_name"],
                "view": item["view"],
                "url": f"/media/generated/{today_str}/{next_index}/{filename}"
            })

        # Async JSON write
        stats_file = os.path.join(json_dir, "stats.json")

        COST_PER_IMAGE = 0.04
        new_images = len(output_urls)

        # Load existing stats or create new
        if os.path.exists(stats_file):
            with open(stats_file, "r") as f:
                stats = json.load(f)
        else:
            stats = {
                "total_images": 0,
                "total_cost": 0.0,
                "history": []
            }

        # Update stats
        stats["total_images"] += new_images
        stats["total_cost"] = round(stats["total_images"] * COST_PER_IMAGE, 2)

        # Create per-request log
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_data = {
            "timestamp": timestamp,
            "gender": gender,
            "bodytype": bodytype,
            "uploaded_images": uploaded_names,
            "generated_images": generated_names,
            "generated_count": new_images,
            "cost_per_image": COST_PER_IMAGE,
            "total_images": stats["total_images"],
            "total_cost": stats["total_cost"]
        }

        # Save per-request JSON
        log_filename = f"generation_{timestamp}.json"
        log_path = os.path.join(json_dir, log_filename)

        with open(log_path, "w") as f:
            json.dump(log_data, f, indent=4)

        # Append history
        stats["history"].append(log_data)

        # Save global stats
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=4)


        return Response({
            "status": "success",
            "count": new_images,
            "results": output_urls,
            "total_images": stats["total_images"],
            "total_cost": stats["total_cost"],
            "date_folder": today_str,
            "hit_folder": next_index 
        })

###-----------------------END DRF API VIEW -----------------------------####