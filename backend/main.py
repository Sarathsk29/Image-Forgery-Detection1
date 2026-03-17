from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import traceback
import json
import os
import tempfile
import base64

from detector.sift_detector import detect_forgery, annotate_image
from detector.ela_detector import detect_ela
from detector.heatmap_generator import generate_heatmap
from detector.report_generator import generate_pdf_report
from detector.document_detector import detect_document_forgery, classify_document, extract_first_page_from_pdf

app = FastAPI(title="Copy-Move Image Forgery Detection", version="1.0.0")

# CORS setup for all origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    print(f"[API] Received file for detection: {file.filename}")
    
    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf')):
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload JPG, PNG, or PDF.")
        
    try:
        image_bytes = await file.read()
        is_pdf = file.filename.lower().endswith('.pdf')
        
        # Check standard document vs image routing
        is_document = is_pdf
        
        if not is_pdf:
            # Check if image looks like a document
            import numpy as np
            import cv2
            image_np = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
            doc_type = classify_document(img)
            if doc_type != "Other":
                is_document = True
                
        if is_document:
            print(f"[API] Routing to Document Analyzer. PDF={is_pdf}")
            # Run the specialized document detector
            sift_result = detect_document_forgery(image_bytes, is_pdf=is_pdf)
            
            # Since detect_document_forgery does not return visual assets natively
            # besides the base SIFT fields, we need to generate them here
            image_bytes_for_visuals = extract_first_page_from_pdf(image_bytes) if is_pdf else image_bytes
            
            ela_result = detect_ela(image_bytes_for_visuals)
            
            annotated_image_base64 = annotate_image(
                sift_result["image"], 
                sift_result["regions"], 
                sift_result["matched_pts"]
            )
            
            heatmap_base64 = generate_heatmap(
                sift_result["image"], 
                sift_result["matched_pts"]
            )
            
            summary = "Document analysis complete."
            if sift_result["is_forged"]:
                summary = f"Possible document forgery detected! Flags: {', '.join(sift_result.get('document_flags', []))}."
            
            original_image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            return {
               "is_forged": sift_result["is_forged"],
               "confidence_score": sift_result["confidence"],
               "method": "Document Forensics (SIFT+ELA+OCR)",
               "keypoints_matched": sift_result["keypoints_matched"],
               "regions": sift_result["regions"],
               "ela_suspicious": ela_result["ela_suspicious"],
               "original_image_base64": original_image_base64,
               "annotated_image_base64": annotated_image_base64,
               "ela_image_base64": ela_result["ela_image_base64"],
               "heatmap_base64": heatmap_base64,
               "summary": summary,
               "document_type": sift_result.get("document_type", "Unknown"),
               "document_flags": sift_result.get("document_flags", []),
               "risk_level": sift_result.get("risk_level", "NONE")
            }
        else:
            print("[API] Routing to Standard Image Analyzer")
            # 1. Run SIFT
            sift_result = detect_forgery(image_bytes)
            
            # 2. Run ELA
            ela_result = detect_ela(image_bytes)
            
            is_forged = sift_result["is_forged"]
            confidence_score = sift_result["confidence"]
            
            # 3. Generate Visuals
            annotated_image_base64 = annotate_image(
                sift_result["image"], 
                sift_result["regions"], 
                sift_result["matched_pts"]
            )
            
            heatmap_base64 = generate_heatmap(
                sift_result["image"], 
                sift_result["matched_pts"]
            )
            
            # 4. Generate Plain English Summary
            if is_forged:
                summary = f"Possible forgery detected! The SIFT algorithm matched {sift_result['keypoints_matched']} keypoint clusters. ELA analysis indicated an anomaly status of {ela_result['ela_suspicious']}."
            else:
                summary = "No significant copy-move forgery was detected based on keypoint matching."
                
            original_image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                
            return {
               "is_forged": is_forged,
               "confidence_score": confidence_score,
               "method": "SIFT+ELA",
               "keypoints_matched": sift_result["keypoints_matched"],
               "regions": sift_result["regions"],
               "ela_suspicious": ela_result["ela_suspicious"],
               "original_image_base64": original_image_base64,
               "annotated_image_base64": annotated_image_base64,
               "ela_image_base64": ela_result["ela_image_base64"],
               "heatmap_base64": heatmap_base64,
               "summary": summary
            }

    except Exception as e:
        print(f"[API] Error in detect endpoint: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

from pydantic import BaseModel
from typing import Dict, Any, Optional

class ReportRequest(BaseModel):
    result_data: Dict[str, Any]
    filename: Optional[str] = "Unknown File"
    date: Optional[str] = ""
    analyst_name: Optional[str] = None
    case_id: Optional[str] = None
    notes: Optional[str] = None

@app.post("/report")
async def report(req: ReportRequest):
    print(f"[API] Generating report for: {req.filename}")
    try:
        data_dict = req.result_data
        metadata = {
            "filename": req.filename or "Unknown File",
            "date": req.date or "",
            "analyst_name": req.analyst_name,
            "case_id": req.case_id,
            "notes": req.notes
        }
        
        pdf_path = generate_pdf_report(data_dict, metadata)
        
        return FileResponse(
            path=pdf_path, 
            filename="forensic_report.pdf", 
            media_type="application/pdf"
        )
    except Exception as e:
        print(f"[API] Error in report endpoint: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
