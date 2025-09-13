from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# ---------- OCRResult Schemas ----------
class OCRResultBase(BaseModel):
    filename: str
    extracted_text: str


class OCRResultCreate(OCRResultBase):
    user_id: str


class OCRResultResponse(OCRResultBase):
    id: int
    user_id: str
    created_at: datetime

    class Config:
        orm_mode = True

# ---------- Document Schemas ----------
class DocumentBase(BaseModel):
    title: str
    content: Optional[str] = None


class DocumentCreate(DocumentBase):
    uploaded_by: str


class DocumentResponse(DocumentBase):
    id: int
    title: str
    content: Optional[str]
    uploaded_by: str
    created_at: datetime

    class Config:
        orm_mode = True

