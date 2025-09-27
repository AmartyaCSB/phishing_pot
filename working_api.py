#!/usr/bin/env python3
"""
Simple, working FastAPI server for email classification
"""

import os
import tempfile
import time
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

# Try to import the classifier, with fallback
try:
    from email_classifier import GemmaEmailClassifier
    CLASSIFIER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Classifier import failed: {e}")
    CLASSIFIER_AVAILABLE = False

# Pydantic models
class TextRequest(BaseModel):
    text: str

class SimpleResult(BaseModel):
    classification: str
    confidence: float
    processing_time_ms: float
    error: Optional[str] = None

class EmailResult(BaseModel):
    filename: str
    classification: str
    confidence: float
    subject: str = ""
    sender: str = ""
    error: Optional[str] = None

class BatchResult(BaseModel):
    results: List[EmailResult]
    total_files: int
    successful: int
    failed: int

# Initialize FastAPI
app = FastAPI(title="Email Classification API", version="1.0.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global classifier
classifier = None

@app.on_event("startup")
async def startup():
    """Initialize classifier"""
    global classifier
    
    if not CLASSIFIER_AVAILABLE:
        print("❌ Classifier not available - running in demo mode")
        return
    
    try:
        print("🚀 Loading classifier...")
        classifier = GemmaEmailClassifier()
        print("✅ Classifier loaded!")
    except Exception as e:
        print(f"❌ Classifier failed to load: {e}")

@app.get("/")
async def root():
    """Serve the beautiful frontend"""
    try:
        with open("frontend.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        # Fallback to simple interface if frontend.html not found
        return HTMLResponse(content="""
        <html><body>
        <h1>Email Classification API</h1>
        <p>Frontend file not found. Please ensure frontend.html exists.</p>
        <p><a href="/docs">View API Documentation</a></p>
        </body></html>
        """)

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "classifier_loaded": classifier is not None,
        "demo_mode": not CLASSIFIER_AVAILABLE
    }

@app.post("/classify/text")
async def classify_text(request: TextRequest):
    """Classify text"""
    if not classifier:
        # Demo response
        return {
            "classification": "phishing",
            "confidence": 0.85,
            "processing_time_ms": 100.0,
            "error": "Demo mode - classifier not loaded"
        }
    
    try:
        start_time = time.time()
        chosen, scores, _ = classifier.classify_text(request.text)
        processing_time = (time.time() - start_time) * 1000
        
        confidence = scores[0][1] if scores else 0.0
        
        return SimpleResult(
            classification=chosen or "unknown",
            confidence=confidence,
            processing_time_ms=processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/classify/email")
async def classify_email(file: UploadFile = File(...)):
    """Classify single email"""
    if not file.filename.lower().endswith('.eml'):
        raise HTTPException(status_code=400, detail="Only .eml files")
    
    if not classifier:
        # Demo response
        return EmailResult(
            filename=file.filename,
            classification="phishing",
            confidence=0.75,
            subject="Demo Subject",
            sender="demo@example.com",
            error="Demo mode"
        )
    
    try:
        content = await file.read()
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.eml', delete=False) as temp:
            temp.write(content)
            temp_path = temp.name
        
        try:
            result = classifier.classify_eml_file(temp_path)
            confidence = result.scores[0][1] if result.scores else 0.0
            
            return EmailResult(
                filename=file.filename,
                classification=result.chosen or "unknown",
                confidence=confidence,
                subject=result.subject or "",
                sender=result.sender or "",
                error=result.error
            )
        finally:
            os.unlink(temp_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/classify/batch")
async def classify_batch(files: List[UploadFile] = File(...)):
    """Classify multiple emails"""
    if len(files) > 20:
        raise HTTPException(status_code=400, detail="Max 20 files")
    
    results = []
    successful = 0
    failed = 0
    
    for file in files:
        try:
            if not file.filename.lower().endswith('.eml'):
                results.append(EmailResult(
                    filename=file.filename,
                    classification="error",
                    confidence=0.0,
                    error="Not .eml file"
                ))
                failed += 1
                continue
            
            if not classifier:
                # Demo response
                results.append(EmailResult(
                    filename=file.filename,
                    classification="spam",
                    confidence=0.65,
                    subject="Demo Subject",
                    error="Demo mode"
                ))
                successful += 1
                continue
            
            content = await file.read()
            
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.eml', delete=False) as temp:
                temp.write(content)
                temp_path = temp.name
            
            try:
                result = classifier.classify_eml_file(temp_path)
                confidence = result.scores[0][1] if result.scores else 0.0
                
                results.append(EmailResult(
                    filename=file.filename,
                    classification=result.chosen or "unknown",
                    confidence=confidence,
                    subject=result.subject or "",
                    sender=result.sender or "",
                    error=result.error
                ))
                
                if result.error:
                    failed += 1
                else:
                    successful += 1
                    
            finally:
                os.unlink(temp_path)
                
        except Exception as e:
            results.append(EmailResult(
                filename=file.filename,
                classification="error",
                confidence=0.0,
                error=str(e)
            ))
            failed += 1
    
    return BatchResult(
        results=results,
        total_files=len(files),
        successful=successful,
        failed=failed
    )

if __name__ == "__main__":
    print("🚀 Starting Working Email Classification API")
    print("📍 http://localhost:8000")
    
    uvicorn.run(
        "working_api:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )
