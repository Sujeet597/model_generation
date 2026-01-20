from google import genai
from google.genai import types
import os
import traceback
from dotenv import load_dotenv
import concurrent.futures
from .promptengine import buildprompt
from .imagelogic import prepareimage
from io import BytesIO
from PIL import Image
import time
import concurrent.futures
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

load_dotenv()

# Initialize the 2025 Client
client = genai.Client(api_key=os.getenv("GEMINIAPI_KEY"))

def run_singlegeneration(shirtfile, gender, bodytype, model, patternfile=None, color_name=None, view_direction="front"):
    try:
        img = Image.open(shirtfile)
        img.load()
        shirtfile.seek(0)
        processed_shirt = prepareimage(shirtfile)
        
        # CRITICAL: Place color lock at the very start
        color_lock_instruction = (
            "Important: The garment color and pattern must remain exactly the same as in the source image. "
            "Do not change shade, tone, or texture. Do not recolor. Do not modify the pattern. "
            "The output must visually match the original garment color and fabric."
        )

        
        if patternfile:
            processed_pattern = prepareimage(patternfile)

            prompt_text = buildprompt(
                'texture overlay',
                gender,
                bodytype,
                model,
                color_name=color_name,
                view_direction=view_direction
            )

            contents = safe_contents(
                color_lock_instruction,
                "Apply the pattern to the garment.",
                processed_shirt,
                processed_pattern,
                prompt_text
            )


        else:
            prompt_text = buildprompt(
                'virtual try on',
                gender,
                bodytype,
                model,
                color_name=color_name,
                view_direction=view_direction
            )

            contents = safe_contents(
                color_lock_instruction,
                "Render the garment on a professional fashion model.",
                processed_shirt,
                prompt_text
            )

        # Use the 2.5 Flash Image model
        response = client.models.generate_content(
            model='gemini-3-pro-image-preview',
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                
           
                safety_settings=[
                    types.SafetySetting(
                        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        threshold="BLOCK_NONE"
                    )
                ]
            )
        )

        # 🚀 CORRECT EXTRACTION FOR 2025 SDK
        # We loop through candidates -> content -> parts
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                # Return the raw bytes or convert to PIL image
                return Image.open(BytesIO(part.inline_data.data))
        
        raise Exception("No image data found in model response.")

    except Exception as e:
        print(f"--- Backend Error ---")
        traceback.print_exc()
        raise e

# def runbatch_pipeline(uploaded_files, gender, bodytype, pattern_file=None,color_name=None, generate_all_views=True):
#     all_results = []
#     views = ["front", "back", "left side", "closeup"] if generate_all_views else ["front"]
    
#     with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
#         future_to_info = {}
        
#         for f in uploaded_files:
#             for view in views:
#                 future = executor.submit(run_singlegeneration, f, gender, bodytype, pattern_file, color_name, view)
#                 future_to_info[future] = {"file_name": f.name, "view": view}
        
#         for future in concurrent.futures.as_completed(future_to_info):
#             info = future_to_info[future]
#             file_name = info["file_name"]
#             view = info["view"]
#             try:
#                 img_obj = future.result()
#                 all_results.append({
#                     "file_name": file_name, 
#                     "view": view,
#                     "output": img_obj
#                 })
#             except Exception as e:
#                 all_results.append({
#                     "file_name": file_name, 
#                     "view": view,
#                     "output": f"Error: {str(e)}"
#                 })
#     return all_results


def safe_contents(*items):
    cleaned = []
    for item in items:
        if item is None:
            continue
        if isinstance(item, (str, Image.Image)):
            cleaned.append(item)
        else:
            raise ValueError(f"Invalid content type: {type(item)}")
    return cleaned

MAX_WORKERS = min(8, os.cpu_count() or 4)
MAX_RETRIES = 2


def runbatch_pipeline(uploaded_files, gender, bodytype, model,  pattern_file=None, color_name=None, generate_all_views=True):
    all_results = []
    views = ["front", "back", "left side", "closeup"] if generate_all_views else ["front"]
    valid_files = []

    # for file in uploaded_files:
    #     try:
    #         img = Image.open(file)
    #         img.verify()   # verify image integrity
    #         file.seek(0)   # reset pointer after verify
    #         valid_files.append(file)
    #     except Exception as e:
    #         print("Skipping invalid image:", file.name, e)

    # uploaded_files = valid_files

    def safe_generate(file, view):
        for attempt in range(MAX_RETRIES):
            try:
                return run_singlegeneration(file, gender, bodytype,model,  pattern_file, color_name, view)
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    raise e
                time.sleep(1)

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []

        for f in uploaded_files:
            for view in views:
                futures.append(executor.submit(safe_generate, f, view))

        for future, (f, view) in zip(futures, [(f, v) for f in uploaded_files for v in views]):
            try:
                img_obj = future.result(timeout=120)

                all_results.append({
                    "file_name": f.name,
                    "view": view,
                    "output": img_obj
                })

            except Exception as e:
                all_results.append({
                    "file_name": f.name,
                    "view": view,
                    "output": f"Error: {str(e)}"
                })

    return all_results