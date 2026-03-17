import cv2
import numpy as np
import base64

def generate_heatmap(img, matched_pts):
    print("[Heatmap] Generating heatmap from matched points...")
    
    if len(matched_pts) == 0:
        # Avoid processing if no matched points, return original image in base64
        _, buffer = cv2.imencode('.png', img)
        return base64.b64encode(buffer).decode('utf-8')

    h, w = img.shape[:2]
    
    # 1. Create a blank mask same size as image
    mask = np.zeros((h, w), dtype=np.uint8)
    
    # 2. Draw filled circles at each matched keypoint location
    for pt in matched_pts:
        cv2.circle(mask, (int(pt[0]), int(pt[1])), 30, (255), -1)
        
    # 3. Apply Gaussian blur (sigma=20)
    mask_blurred = cv2.GaussianBlur(mask, (0, 0), sigmaX=20, sigmaY=20)
    
    # 4. Apply colormap (cv2.COLORMAP_JET)
    heatmap_colored = cv2.applyColorMap(mask_blurred, cv2.COLORMAP_JET)
    
    # 5. Blend with original image at alpha=0.4
    alpha = 0.4
    blended = cv2.addWeighted(heatmap_colored, alpha, img, 1 - alpha, 0)
    
    _, buffer = cv2.imencode('.png', blended)
    return base64.b64encode(buffer).decode('utf-8')
