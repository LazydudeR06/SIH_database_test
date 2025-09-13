from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import easyocr
import cv2
import os
import tempfile
import shutil

# Local imports
from .db import get_db
from .clerk import get_current_user
from .validator import check_authenticity
from .audit import log_access
from .models import DocumentORM, OCRResult
from .schemas import (
    DocumentCreate, DocumentResponse,
    OCRResultResponse
)

# Initialize FastAPI once
app = FastAPI(title="Academic & Degree Verifier", version="1.0")

# Initialize EasyOCR reader once (expensive to reload every request)
reader = easyocr.Reader(['en', 'hi'], gpu=False)


# ---------- Utility ----------
def preprocess_image(image_path: str) -> str:
    """
    Preprocess image using OpenCV:
    - Convert to grayscale
    - Apply binary threshold
    - Save processed image
    """
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if img is None:
        return image_path  # fallback if not a valid image

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    processed_fd, processed_path = tempfile.mkstemp(suffix=".jpg")
    os.close(processed_fd)
    cv2.imwrite(processed_path, thresh)

    return processed_path


# ---------- Routes ----------
@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "Academic Authenticity & Degree Verifier API running"
    }


@app.post("/check-authenticity", response_model=DocumentResponse)
def validate_document(
    doc: DocumentCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Validate a document’s authenticity and save to DB
    """
    is_original = check_authenticity(doc.content)

    new_doc = DocumentORM(
        title=doc.title,
        content=doc.content,
        uploaded_by=user["user_id"]
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    log_access(user["user_id"], "CHECK_DOCUMENT", doc.title)

    return new_doc


@app.post("/upload-document", response_model=DocumentResponse)
def upload_file(
    doc: DocumentCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a new document (only professors/admins allowed)
    """
    if user["role"] not in ["professor", "admin"]:
        raise HTTPException(status_code=403, detail="Only faculty/admins can upload documents")

    new_doc = DocumentORM(
        title=doc.title,
        content=doc.content,
        uploaded_by=user["user_id"]
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    log_access(user["user_id"], "UPLOAD_DOCUMENT", doc.title)

    return new_doc


@app.get("/dashboard")
def dashboard(user=Depends(get_current_user)):
    log_access(user["user_id"], "VIEW_DASHBOARD", user["role"])
    return {"message": f"Welcome {user['role'].capitalize()} {user['user_id']}"}


@app.post("/upload", response_model=OCRResultResponse)
async def upload_and_ocr(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Handles image upload + OCR:
    - Saves to a temporary file
    - Preprocesses with OpenCV
    - Extracts text with EasyOCR
    - Saves OCR result to DB (Supabase/Postgres)
    - Deletes temp files after processing
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = file.filename.lower().split(".")[-1]
    if ext not in ["jpg", "jpeg", "png"]:
        raise HTTPException(status_code=400, detail="Only JPG/PNG images are supported")

    suffix = "." + ext
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=suffix)
    os.close(tmp_fd)

    with open(tmp_path, "wb") as tmp:
        shutil.copyfileobj(file.file, tmp)

    try:
        processed_path = preprocess_image(tmp_path)
        results = reader.readtext(processed_path, detail=0)

        new_record = OCRResult(
            filename=file.filename,
            extracted_text=" ".join(results),
            user_id=user["user_id"]
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if 'processed_path' in locals() and os.path.exists(processed_path):
            os.remove(processed_path)

    log_access(user["user_id"], "UPLOAD_DOCUMENT", file.filename)

    return new_record
