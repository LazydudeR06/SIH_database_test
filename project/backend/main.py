from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from models import Document
from clerk import get_current_user
from validator import check_authenticity
from audit import log_access

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to Academic Authenticity Validator"}

@app.post("/check-authenticity")
def validate_document(doc: Document, user=Depends(get_current_user)):
    is_original = check_authenticity(doc.content)
    log_access(user["user_id"], "CHECK_DOCUMENT", doc.title)
    return {"title": doc.title, "is_original": is_original, "checked_by": user["user_id"]}

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
