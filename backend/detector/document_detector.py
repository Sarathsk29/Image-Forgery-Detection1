import cv2
import numpy as np
import io
from PIL import Image
import fitz  # PyMuPDF
from detector.sift_detector import detect_forgery

def extract_first_page_from_pdf(pdf_bytes: bytes) -> bytes:
    """
    Extracts the first page of a PDF and returns it as JPEG image bytes.
    """
    try:
        # Open the PDF from bytes
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        if pdf_document.page_count == 0:
            raise ValueError("PDF document has no pages.")
        
        # Load first page
        page = pdf_document.load_page(0)
        
        # Render page to an image (pixmap) at 300 DPI for good resolution
        zoom = 2.0 
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # Convert pixmap to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Save PIL Image to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=95)
        return img_byte_arr.getvalue()
        
    except Exception as e:
        raise ValueError(f"Failed to extract image from PDF: {str(e)}")

def classify_document(image: np.ndarray) -> str:
    """
    Classifies if an image looks like a specific type of document based on heuristics
    like white space ratio and contour density.
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Calculate whitespace ratio (pixels close to white)
    white_pixels = np.sum(gray > 240)
    total_pixels = gray.size
    whitespace_ratio = white_pixels / total_pixels
    
    # Use adaptive thresholding to find text-like regions
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Count small/medium contours which often represent text characters
    text_contours = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 10 < area < 1000:
            text_contours += 1
            
    # Simple heuristic classification
    if whitespace_ratio > 0.6 and text_contours > 200:
        return "Legal Document"
    elif whitespace_ratio > 0.4 and 50 < text_contours < 300:
        return "Certificate"
    elif whitespace_ratio < 0.3 and text_contours > 20: # Example logic for ID
        return "ID Card"
        
    return "Other"

def analyze_signature_region(image: np.ndarray, ela_image: np.ndarray) -> bool:
    """
    Analyzes the bottom 20% of the document for suspicious ELA activity
    which might indicate signature manipulation.
    """
    height, width = image.shape[:2]
    
    # Define bottom 20% region
    y_start = int(height * 0.8)
    
    # Crop regions
    sig_region_rgb = image[y_start:height, 0:width]
    sig_region_ela = ela_image[y_start:height, 0:width]
    
    # Look for dark strokes (signatures are usually dark ink)
    gray = cv2.cvtColor(sig_region_rgb, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
    stroke_pixels = np.sum(binary == 255)
    
    if stroke_pixels < 500:
        # No significant dark strokes found, probably no signature here
        return False
        
    # Check ELA intensity precisely where the dark strokes are
    # If the stroke pixels themselves have unusually high ELA, they might be pasted
    stroke_mask = binary == 255
    ela_in_strokes = np.mean(sig_region_ela[stroke_mask])
    
    # Check background ELA
    bg_mask = binary == 0
    ela_in_bg = np.mean(sig_region_ela[bg_mask])
    
    # If strokes have significantly higher ELA than background, it's suspicious
    # Constants here are illustrative thresholds
    if ela_in_strokes > (ela_in_bg * 1.5) and ela_in_strokes > 40:
        return True
        
    return False

def detect_stamps_and_seals(image: np.ndarray, ela_image: np.ndarray) -> bool:
    """
    Detects circular regions (common for official stamps/seals) and checks
    if their ELA score is suspicious.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Blur to reduce noise for circle detection
    blurred = cv2.medianBlur(gray, 5)
    
    # Find circles using Hough transform
    circles = cv2.HoughCircles(
        blurred, 
        cv2.HOUGH_GRADIENT, 
        dp=1, 
        minDist=100, 
        param1=50, 
        param2=30, 
        minRadius=30, 
        maxRadius=200
    )
    
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            x, y, r = i[0], i[1], i[2]
            
            # Ensure coordinates are within image bounds
            height, width = image.shape[:2]
            x_min, x_max = max(0, x - r), min(width, x + r)
            y_min, y_max = max(0, y - r), min(height, y + r)
            
            if x_max <= x_min or y_max <= y_min:
                continue
                
            # Extract ELA region for the circle bounding box
            circle_ela = ela_image[y_min:y_max, x_min:x_max]
            
            # Simple global average comparison
            global_ela_mean = np.mean(ela_image)
            circle_ela_mean = np.mean(circle_ela)
            
            # If the stamp region has heavily varied compression compared to the rest of the document
            if circle_ela_mean > (global_ela_mean * 1.8) and circle_ela_mean > 30:
                return True
                
    return False

def analyze_text_blocks(image: np.ndarray, ela_image: np.ndarray) -> bool:
    """
    Detects text blocks and checks for inconsistent ELA values between blocks.
    A block with a significantly different ELA might be a pasted paragraph.
    """
    # Quick text block detection using dilation
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    
    # Dilate to connect text characters into blocks
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 5))
    dilated = cv2.dilate(thresh, kernel, iterations=3)
    
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    block_ela_means = []
    
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # Filter for moderately sized blocks (paragraphs/lines)
        if w > 100 and h > 20 and w * h < (image.shape[0] * image.shape[1] * 0.5):
            block_ela = ela_image[y:y+h, x:x+w]
            mean_ela = np.mean(block_ela)
            block_ela_means.append(mean_ela)
            
    if len(block_ela_means) > 3:
        # Calculate standard deviation of block ELA means
        ela_std = np.std(block_ela_means)
        ela_mean_all = np.mean(block_ela_means)
        
        # Find max outlier
        max_block_ela = max(block_ela_means)
        
        # If one block is vastly different from the average block ELA
        if max_block_ela > (ela_mean_all + 2 * ela_std) and max_block_ela > 40:
             return True
             
    return False

def detect_document_forgery(image_bytes: bytes, is_pdf: bool = False) -> dict:
    """
    Main entry point for document-specific forgery detection.
    """
    try:
        if is_pdf:
            image_bytes = extract_first_page_from_pdf(image_bytes)
            
        # 1. Run standard SIFT algorithm (this returns standard visual artifacts too)
        sift_result = detect_forgery(image_bytes)
        
        # Get raw OpenCV arrays for further document processing
        image_np = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        
        # We need ELA image array for advanced checks. 
        # (detect_forgery in main orchestrator calls detect_ela separately usually, 
        # but since we're in a specialized module, let's call it to get the raw numpy array)
        from detector.ela_detector import run_ela
        ela_image_cv2 = run_ela(image_bytes)
        
        # 2. Document Classification
        doc_type = classify_document(image)
        
        # 3. Document-Specific Forensic Checks
        flags = []
        is_forged = sift_result["is_forged"]  # Start with SIFT verdict
        
        if sift_result["is_forged"]:
            flags.append(f"Copy-Move manipulation detected ({sift_result['keypoints_matched']} matched regions).")
        
        # Signature Check
        sig_suspicious = analyze_signature_region(image, ela_image_cv2)
        if sig_suspicious:
            flags.append("Signature area shows suspicious ELA anomalies (potential manipulation).")
            is_forged = True
            
        # Stamp/Seal Check
        stamp_suspicious = detect_stamps_and_seals(image, ela_image_cv2)
        if stamp_suspicious:
            flags.append("Circular stamp/seal region shows abnormal compression artifacts.")
            is_forged = True
            
        # Text Block Consistency
        text_suspicious = analyze_text_blocks(image, ela_image_cv2)
        if text_suspicious:
            flags.append("Inconsistent text block ELA detected (potential digital text replacement).")
            is_forged = True
            
        # 4. Determine Risk Level
        risk_level = "NONE"
        if len(flags) > 2:
            risk_level = "HIGH"
        elif len(flags) > 0:
            risk_level = "MEDIUM"
            
        # 5. Build Enhanced Result JSON
        result = sift_result.copy() # Inherit standard keys (image, keypoints_matched, confidence)
        result["is_forged"] = is_forged
        
        # Adjust confidence upward if multiple document flags hit
        if len(flags) > 1 and result["confidence"] < 0.8:
             result["confidence"] = min(0.95, result["confidence"] + 0.3)
             
        result["document_type"] = doc_type
        result["document_flags"] = flags
        result["risk_level"] = risk_level
        result["is_pdf_extracted"] = is_pdf
        
        return result
        
    except Exception as e:
        import traceback
        print(f"[ERROR] Document Analysis Failed: {traceback.format_exc()}")
        raise ValueError(f"Document processing failed: {str(e)}")
