import cv2
import numpy as np
import base64

def run_ela(image_bytes):
    # Read image from bytes
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Could not decode image.")
        
    # 1. Save image at quality 90 as JPEG buffer
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    _, encoded_img = cv2.imencode('.jpg', img, encode_param)
    
    # Decode the compressed image
    compressed_img = cv2.imdecode(encoded_img, cv2.IMREAD_COLOR)
    
    # 2. Compute pixel difference between original and re-saved
    diff = cv2.absdiff(img, compressed_img)
    diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    
    # 3. Amplify difference by factor 10
    amplified_diff = cv2.convertScaleAbs(diff_gray, alpha=10.0, beta=0)
    
    return amplified_diff

def detect_ela(image_bytes):
    print("[ELA] Starting Error Level Analysis...")
    
    amplified_diff = run_ela(image_bytes)
    
    # 4. Calculate mean ELA value
    mean_ela = np.mean(amplified_diff)
    print(f"[ELA] Mean ELA value: {mean_ela:.2f}")
    
    # 5. Flag suspicious if mean ELA > 8.0
    ela_suspicious = bool(mean_ela > 8.0)
    
    # Encode ELA image for response (with JET colormap for visualization)
    ela_color = cv2.applyColorMap(amplified_diff, cv2.COLORMAP_JET)
    _, buffer = cv2.imencode('.png', ela_color)
    ela_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return {
        "ela_suspicious": ela_suspicious,
        "mean_ela": mean_ela,
        "ela_image_base64": ela_base64
    }
