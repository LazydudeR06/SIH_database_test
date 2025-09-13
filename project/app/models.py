from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from .db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)   # Clerk user ID
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, default="student")  # "student", "professor", "admin"

    documents = relationship("DocumentORM", back_populates="uploader")
    ocr_results = relationship("OCRResult", back_populates="user")

class DocumentORM(Base):   # Changed from Document to DocumentORM to match your import
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)  # Optional raw content
    uploaded_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    uploader = relationship("User", back_populates="documents")

class OCRResult(Base):
    __tablename__ = "ocr_results"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    extracted_text = Column(Text, nullable=False)
    user_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="ocr_results")