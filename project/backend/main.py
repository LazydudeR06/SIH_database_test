from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from models import Document
from clerk import get_current_user
from validator import check_authenticity
from audit import log_access
import easyocr
import cv2
import os
import tempfile
import shutil

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

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply threshold (binarization)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # Save processed image to a temporary path
    processed_fd, processed_path = tempfile.mkstemp(suffix=".jpg")
    os.close(processed_fd)  # close file descriptor
    cv2.imwrite(processed_path, thresh)

    return processed_path


# ---------- Routes ----------
@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "Academic Authenticity & Degree Verifier API running"
    }


@app.post("/check-authenticity")
def validate_document(doc: Document, user=Depends(get_current_user)):
    is_original = check_authenticity(doc.content)
    log_access(user["user_id"], "CHECK_DOCUMENT", doc.title)
    return {
        "title": doc.title,
        "is_original": is_original,
        "checked_by": user["user_id"]
    }


@app.post("/upload-document")
def upload_file(file: UploadFile = File(...), user=Depends(get_current_user)):
    if user["role"] not in ["professor", "admin"]:
        raise HTTPException(status_code=403, detail="Only faculty/admins can upload documents")
    log_access(user["user_id"], "UPLOAD_DOCUMENT", file.filename)
    return {"filename": file.filename, "uploaded_by": user["user_id"]}


@app.get("/dashboard")
def dashboard(user=Depends(get_current_user)):
    log_access(user["user_id"], "VIEW_DASHBOARD", user["role"])
    return {"message": f"Welcome {user['role'].capitalize()} {user['user_id']}"}


@app.post("/upload")
async def upload_and_ocr(file: UploadFile = File(...)):
    """
    Handles image upload:
    - Saves to a temporary file
    - Preprocesses with OpenCV
    - Extracts text with EasyOCR
    - Deletes temp files after processing
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Ensure it's an image
    ext = file.filename.lower().split(".")[-1]
    if ext not in ["jpg", "jpeg", "png"]:
        raise HTTPException(status_code=400, detail="Only JPG/PNG images are supported")

    # Create a temporary file for the uploaded image
    suffix = "." + ext
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=suffix)
    os.close(tmp_fd)

    with open(tmp_path, "wb") as tmp:
        shutil.copyfileobj(file.file, tmp)

    try:
        # Preprocess image with OpenCV
        processed_path = preprocess_image(tmp_path)

        # Run OCR
        results = reader.readtext(processed_path, detail=0)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")

    finally:
        # Cleanup temp files
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if 'processed_path' in locals() and os.path.exists(processed_path):
            os.remove(processed_path)

    return {"filename": file.filename, "ocr_text": results}
