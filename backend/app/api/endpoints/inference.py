from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.services.inference_service import YOLOInferenceService

router = APIRouter()

@router.post("/image", summary="Run YOLOv8 road defect detection on an uploaded dashcam frame")
async def detect_frame_defects(
    file: UploadFile = File(...),
    confidence: float = Form(0.65)
):
    # Validate extension
    allowed_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]
    filename = file.filename or "image.jpg"
    ext = filename.lower()[filename.rfind("."):]
    
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format '{ext}'. Allowed: {', '.join(allowed_extensions)}"
        )

    image_bytes = await file.read()
    
    # Enforce 15MB frame limit
    if len(image_bytes) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image exceeds 15 MB limit.")

    try:
        result = YOLOInferenceService.run_image_inference(
            image_bytes=image_bytes,
            confidence_threshold=confidence
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference execution failed: {str(e)}")

