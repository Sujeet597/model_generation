from PIL import Image
import io

def prepareimage(uploaded_file):
    try:
        img = Image.open(uploaded_file)
        img_rgb = img.convert("RGB")
        
       
        width, height = img_rgb.size

        new_height = int(height * 1.20) 
        
        
        padded_img = Image.new("RGB", (width, new_height), (255, 255, 255))
        
    
        padded_img.paste(img_rgb, (0, 0))
        
        return padded_img
        
    except Exception as e:
        print(f"Error processing image: {e}")
        return None