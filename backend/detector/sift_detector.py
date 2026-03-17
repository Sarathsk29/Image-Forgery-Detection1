import cv2
import numpy as np
import base64

def detect_forgery(image_bytes):
    print("[SIFT] Starting SIFT detection...")
    
    # Read image from bytes
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Could not decode image.")
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 1. Initialize SIFT detector
    sift = cv2.SIFT_create(nfeatures=500)
    keypoints, descriptors = sift.detectAndCompute(gray, None)
    
    if descriptors is None:
        return {"is_forged": False, "confidence": 0.0, "keypoints_matched": 0, "regions": [], "matched_pts": [], "image": img}
        
    if len(descriptors) < 2:
        return {"is_forged": False, "confidence": 0.0, "keypoints_matched": 0, "regions": [], "matched_pts": [], "image": img}
        
    # Convert to list to avoid 'Sized' type indexing errors in Pyright
    keypoints = list(keypoints) # type: ignore
        
    print(f"[SIFT] Found {len(keypoints)} keypoints.")
    
    # 2. Use FLANN matcher with KDTree (algorithm=1, trees=5)
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    
    # Match descriptors to themselves to find duplicates
    matches = flann.knnMatch(descriptors, descriptors, k=3)
    
    good_matches = []
    # 3. Apply Lowe's ratio test: ratio = 0.75
    for match in matches:
        if len(match) >= 3:
            # match[0] is the descriptor matching itself
            # match[1] is the closest match
            # match[2] is the second closest match
            if match[1].distance < 0.75 * match[2].distance:
                # Ensure distance between points is significant (not adjacent keypoints)
                pt1 = keypoints[match[0].queryIdx].pt
                pt2 = keypoints[match[1].trainIdx].pt
                dist = np.linalg.norm(np.array(pt1) - np.array(pt2))
                if dist > 10:
                    good_matches.append(match[1])

    print(f"[SIFT] Found {len(good_matches)} good matches after ratio test.")
    
    is_forged = False
    confidence = 0.0
    regions = []
    matched_pts = []
    
    # 4. Apply RANSAC homography filtering: ransacReprojThreshold=5.0
    if len(good_matches) > 10:
        src_pts = np.float32([keypoints[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([keypoints[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        
        if mask is not None:
            matchesMask = mask.ravel().tolist()
            inliers = sum(matchesMask)
            print(f"[SIFT] Found {inliers} inliers after RANSAC.")
            
            # 5. Mark a region as forged if matched keypoints > 10
            if inliers > 10:
                is_forged = True
                
                # 6. Return confidence = min(1.0, matched_pairs / 50)
                confidence = min(1.0, float(inliers) / 50.0)
                
                # 7. Draw bounding boxes around matched keypoint clusters
                # Getting matched points for heatmap & bounding boxes
                inlier_pts = []
                for i, m in enumerate(matchesMask):
                    if m:
                        pt1 = keypoints[good_matches[i].trainIdx].pt
                        pt2 = keypoints[good_matches[i].queryIdx].pt
                        matched_pts.extend([pt1, pt2])
                        inlier_pts.append(pt1) # Simplified region logic using destination points
                
                if inlier_pts:
                    inlier_pts = np.array(inlier_pts)
                    x, y, w, h = cv2.boundingRect(np.float32(inlier_pts))
                    regions.append({"x": int(x), "y": int(y), "w": int(w), "h": int(h), "label": "copied_region"})

    return {
        "is_forged": is_forged,
        "confidence": confidence,
        "keypoints_matched": len(good_matches),
        "regions": regions,
        "matched_pts": matched_pts,
        "image": img
    }

def annotate_image(img, regions, matched_pts):
    annotated = img.copy()
    
    # Draw keypoint circles if there are any
    for pt in matched_pts:
        cv2.circle(annotated, (int(pt[0]), int(pt[1])), 4, (0, 0, 255), -1)
        
    # Draw boxes
    for r in regions:
        cv2.rectangle(annotated, (r['x'], r['y']), (r['x']+r['w'], r['y']+r['h']), (0, 255, 0), 3)
        cv2.putText(annotated, r['label'], (r['x'], r['y'] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
    _, buffer = cv2.imencode('.png', annotated)
    return base64.b64encode(buffer).decode('utf-8')
