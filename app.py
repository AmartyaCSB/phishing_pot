#!/usr/bin/env python3
"""
Email Classification Microservice API
FastAPI-based microservice for email classification using Gemma model
"""

import os
import time
import logging
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from classifier_service import get_classifier_service, EmailClassifierService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API
class ClassificationResponse(BaseModel):
    file_name: str
    classification: Optional[str]
    confidence_scores: List[dict]
    metadata: dict
    processing_time_ms: float
    model_version: str
    error: Optional[str] = None

class BatchClassificationResponse(BaseModel):
    results: List[ClassificationResponse]
    total_files: int
    successful_classifications: int
    failed_classifications: int
    total_processing_time_ms: float

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_id: str
    uptime_stats: dict

class StatsResponse(BaseModel):
    total_classifications: int
    cache_hits: int
    errors: int
    avg_processing_time: float
    model_loaded: bool
    model_id: str
    labels: List[str]
    cache_size: int

# Initialize FastAPI app
app = FastAPI(
    title="Email Classification API",
    description="Microservice for classifying emails as phishing, spam, or benign using Gemma-3-270m-it model",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global classifier service
classifier_service: Optional[EmailClassifierService] = None

@app.on_event("startup")
async def startup_event():
    """Initialize the classifier service on startup"""
    global classifier_service
    try:
        logger.info("🚀 Starting Email Classification API...")
        classifier_service = get_classifier_service()
        logger.info("✅ Classifier service initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize classifier service: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Email Classification API...")

# API Routes

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email Classification API</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container {
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            h1 {
                color: #4a5568;
                text-align: center;
                margin-bottom: 30px;
            }
            .upload-area {
                border: 3px dashed #cbd5e0;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                margin: 20px 0;
                transition: all 0.3s ease;
            }
            .upload-area:hover {
                border-color: #667eea;
                background-color: #f7fafc;
            }
            .btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
                transition: transform 0.2s;
            }
            .btn:hover {
                transform: translateY(-2px);
            }
            .result {
                margin-top: 20px;
                padding: 20px;
                border-radius: 10px;
                background-color: #f8f9fa;
            }
            .classification {
                font-size: 24px;
                font-weight: bold;
                margin: 10px 0;
            }
            .phishing { color: #e53e3e; }
            .spam { color: #dd6b20; }
            .benign { color: #38a169; }
            .metadata {
                background: #edf2f7;
                padding: 15px;
                border-radius: 8px;
                margin-top: 15px;
            }
            .api-links {
                text-align: center;
                margin-top: 30px;
            }
            .api-links a {
                margin: 0 15px;
                color: #667eea;
                text-decoration: none;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ Email Classification API</h1>
            <p style="text-align: center; color: #666; font-size: 18px;">
                Upload an email (.eml) file to classify it as <strong>phishing</strong>, <strong>spam</strong>, or <strong>benign</strong>
            </p>
            
            <div class="upload-area" id="uploadArea">
                <p>📧 Drag and drop your .eml file(s) here or click to browse</p>
                <input type="file" id="fileInput" accept=".eml" multiple style="display: none;">
                <button class="btn" onclick="document.getElementById('fileInput').click()">
                    Choose File(s)
                </button>
                <p style="font-size: 14px; color: #666; margin-top: 10px;">
                    💡 Select multiple files for batch processing
                </p>
            </div>
            
            <div style="text-align: center; margin: 20px 0;">
                <button class="btn" id="uploadBtn" onclick="uploadFile()" disabled>
                    🔍 Classify Email
                </button>
            </div>
            
            <div id="result" class="result" style="display: none;"></div>
            
            <div class="api-links">
                <a href="/docs" target="_blank">📚 API Documentation</a>
                <a href="/health">🏥 Health Check</a>
                <a href="/stats">📊 Statistics</a>
            </div>
        </div>

        <script>
            const fileInput = document.getElementById('fileInput');
            const uploadBtn = document.getElementById('uploadBtn');
            const uploadArea = document.getElementById('uploadArea');
            const result = document.getElementById('result');
            
            fileInput.addEventListener('change', function(e) {
                if (e.target.files.length > 0) {
                    uploadBtn.disabled = false;
                    const fileCount = e.target.files.length;
                    if (fileCount === 1) {
                        uploadArea.innerHTML = `<p>📧 Selected: ${e.target.files[0].name}</p>`;
                        uploadBtn.textContent = '🔍 Classify Email';
                    } else {
                        uploadArea.innerHTML = `<p>📧 Selected: ${fileCount} files</p>`;
                        uploadBtn.textContent = `🔍 Classify ${fileCount} Emails`;
                    }
                }
            });
            
            // Drag and drop functionality
            uploadArea.addEventListener('dragover', function(e) {
                e.preventDefault();
                uploadArea.style.borderColor = '#667eea';
                uploadArea.style.backgroundColor = '#f7fafc';
            });
            
            uploadArea.addEventListener('dragleave', function(e) {
                e.preventDefault();
                uploadArea.style.borderColor = '#cbd5e0';
                uploadArea.style.backgroundColor = 'white';
            });
            
            uploadArea.addEventListener('drop', function(e) {
                e.preventDefault();
                uploadArea.style.borderColor = '#cbd5e0';
                uploadArea.style.backgroundColor = 'white';
                
                const files = e.dataTransfer.files;
                const emlFiles = Array.from(files).filter(f => f.name.endsWith('.eml'));
                
                if (emlFiles.length > 0) {
                    fileInput.files = files;
                    uploadBtn.disabled = false;
                    
                    if (emlFiles.length === 1) {
                        uploadArea.innerHTML = `<p>📧 Selected: ${emlFiles[0].name}</p>`;
                        uploadBtn.textContent = '🔍 Classify Email';
                    } else {
                        uploadArea.innerHTML = `<p>📧 Selected: ${emlFiles.length} .eml files</p>`;
                        uploadBtn.textContent = `🔍 Classify ${emlFiles.length} Emails`;
                    }
                } else {
                    uploadArea.innerHTML = `<p style="color: red;">❌ Please select .eml files only</p>`;
                }
            });
            
            async function uploadFile() {
                const files = fileInput.files;
                if (!files || files.length === 0) return;
                
                uploadBtn.disabled = true;
                uploadBtn.textContent = '🔄 Processing...';
                result.style.display = 'none';
                
                const formData = new FormData();
                
                try {
                    if (files.length === 1) {
                        // Single file upload
                        formData.append('file', files[0]);
                        
                        const response = await fetch('/classify/upload', {
                            method: 'POST',
                            body: formData
                        });
                        
                        const data = await response.json();
                        displaySingleResult(data);
                    } else {
                        // Batch upload
                        for (let i = 0; i < files.length; i++) {
                            formData.append('files', files[i]);
                        }
                        
                        const response = await fetch('/classify/batch', {
                            method: 'POST',
                            body: formData
                        });
                        
                        const data = await response.json();
                        displayBatchResults(data);
                    }
                } catch (error) {
                    result.innerHTML = `<div style="color: red;">❌ Error: ${error.message}</div>`;
                    result.style.display = 'block';
                } finally {
                    uploadBtn.disabled = false;
                    uploadBtn.textContent = files.length === 1 ? '🔍 Classify Email' : `🔍 Classify ${files.length} Emails`;
                }
            }
            
            function displaySingleResult(data) {
                if (data.error) {
                    result.innerHTML = `<div style="color: red;">❌ Error: ${data.error}</div>`;
                } else {
                    const classification = data.classification || 'unknown';
                    const confidence = data.confidence_scores.length > 0 ? 
                        (data.confidence_scores[0].score * 100).toFixed(1) : 'N/A';
                    
                    result.innerHTML = `
                        <h3>Classification Result</h3>
                        <div class="classification ${classification}">
                            🏷️ ${classification.toUpperCase()}
                        </div>
                        <p><strong>Confidence:</strong> ${confidence}%</p>
                        <p><strong>Processing Time:</strong> ${data.processing_time_ms}ms</p>
                        
                        <div class="metadata">
                            <h4>📧 Email Metadata</h4>
                            <p><strong>Subject:</strong> ${data.metadata.subject || 'N/A'}</p>
                            <p><strong>From:</strong> ${data.metadata.sender || 'N/A'}</p>
                            <p><strong>To:</strong> ${data.metadata.recipient || 'N/A'}</p>
                        </div>
                        
                        <details style="margin-top: 15px;">
                            <summary>🔍 Detailed Scores</summary>
                            <pre>${JSON.stringify(data.confidence_scores, null, 2)}</pre>
                        </details>
                    `;
                }
                result.style.display = 'block';
            }
            
            function displayBatchResults(data) {
                if (!data.results || data.results.length === 0) {
                    result.innerHTML = `<div style="color: red;">❌ No results received</div>`;
                    result.style.display = 'block';
                    return;
                }
                
                const totalFiles = data.total_files;
                const successful = data.successful_classifications;
                const failed = data.failed_classifications;
                const totalTime = data.total_processing_time_ms;
                
                let html = `
                    <h3>Batch Classification Results</h3>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                        <p><strong>📊 Summary:</strong></p>
                        <p>• Total Files: ${totalFiles}</p>
                        <p>• Successful: ${successful}</p>
                        <p>• Failed: ${failed}</p>
                        <p>• Total Processing Time: ${totalTime.toFixed(0)}ms</p>
                        <p>• Average Time per File: ${(totalTime / totalFiles).toFixed(0)}ms</p>
                    </div>
                    
                    <div style="max-height: 400px; overflow-y: auto;">
                `;
                
                data.results.forEach((item, index) => {
                    const classification = item.classification || 'unknown';
                    const confidence = item.confidence_scores.length > 0 ? 
                        (item.confidence_scores[0].score * 100).toFixed(1) : 'N/A';
                    
                    html += `
                        <div style="border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 8px; background: white;">
                            <h4 style="margin: 0 0 10px 0;">📧 ${item.file_name}</h4>
                            <div class="classification ${classification}" style="font-size: 18px; margin: 10px 0;">
                                🏷️ ${classification.toUpperCase()}
                            </div>
                            <p><strong>Confidence:</strong> ${confidence}%</p>
                            <p><strong>Processing Time:</strong> ${item.processing_time_ms}ms</p>
                            ${item.error ? `<p style="color: red;"><strong>Error:</strong> ${item.error}</p>` : ''}
                            
                            <details style="margin-top: 10px;">
                                <summary>📧 Email Details</summary>
                                <div style="margin-top: 10px; font-size: 14px;">
                                    <p><strong>Subject:</strong> ${item.metadata.subject || 'N/A'}</p>
                                    <p><strong>From:</strong> ${item.metadata.sender || 'N/A'}</p>
                                    <p><strong>To:</strong> ${item.metadata.recipient || 'N/A'}</p>
                                </div>
                            </details>
                        </div>
                    `;
                });
                
                html += '</div>';
                result.innerHTML = html;
                result.style.display = 'block';
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    if not classifier_service:
        raise HTTPException(status_code=503, detail="Classifier service not initialized")
    
    health_data = classifier_service.health_check()
    return HealthResponse(**health_data)

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get service statistics"""
    if not classifier_service:
        raise HTTPException(status_code=503, detail="Classifier service not initialized")
    
    stats_data = classifier_service.get_stats()
    return StatsResponse(**stats_data)

@app.post("/classify/upload", response_model=ClassificationResponse)
async def classify_upload(file: UploadFile = File(...)):
    """
    Upload and classify a single email file
    """
    if not classifier_service:
        raise HTTPException(status_code=503, detail="Classifier service not initialized")
    
    # Validate file
    if not file.filename.endswith('.eml'):
        raise HTTPException(status_code=400, detail="Only .eml files are supported")
    
    # Check file size (max 10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB")
    
    try:
        # Classify the email
        result = classifier_service.classify_bytes(content, file.filename)
        return ClassificationResponse(**result)
    
    except Exception as e:
        logger.error(f"Classification error: {e}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@app.post("/classify/batch", response_model=BatchClassificationResponse)
async def classify_batch(files: List[UploadFile] = File(...)):
    """
    Upload and classify multiple email files
    """
    if not classifier_service:
        raise HTTPException(status_code=503, detail="Classifier service not initialized")
    
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per batch")
    
    results = []
    successful = 0
    failed = 0
    total_time = 0
    
    for file in files:
        if not file.filename.endswith('.eml'):
            results.append(ClassificationResponse(
                file_name=file.filename,
                classification=None,
                confidence_scores=[],
                metadata={},
                processing_time_ms=0,
                model_version=classifier_service.model_id,
                error="Only .eml files are supported"
            ))
            failed += 1
            continue
        
        try:
            content = await file.read()
            if len(content) > 10 * 1024 * 1024:
                results.append(ClassificationResponse(
                    file_name=file.filename,
                    classification=None,
                    confidence_scores=[],
                    metadata={},
                    processing_time_ms=0,
                    model_version=classifier_service.model_id,
                    error="File too large. Maximum size is 10MB"
                ))
                failed += 1
                continue
            
            result = classifier_service.classify_bytes(content, file.filename)
            results.append(ClassificationResponse(**result))
            total_time += result['processing_time_ms']
            
            if result['error']:
                failed += 1
            else:
                successful += 1
                
        except Exception as e:
            logger.error(f"Batch classification error for {file.filename}: {e}")
            results.append(ClassificationResponse(
                file_name=file.filename,
                classification=None,
                confidence_scores=[],
                metadata={},
                processing_time_ms=0,
                model_version=classifier_service.model_id,
                error=str(e)
            ))
            failed += 1
    
    return BatchClassificationResponse(
        results=results,
        total_files=len(files),
        successful_classifications=successful,
        failed_classifications=failed,
        total_processing_time_ms=total_time
    )

@app.delete("/cache")
async def clear_cache():
    """Clear the classification cache"""
    if not classifier_service:
        raise HTTPException(status_code=503, detail="Classifier service not initialized")
    
    classifier_service.clear_cache()
    return {"message": "Cache cleared successfully"}

@app.get("/models")
async def get_models():
    """Get information about available models"""
    return {
        "current_model": {
            "id": "google/gemma-3-270m-it",
            "name": "Gemma 3 270M Instruction Tuned",
            "description": "Google's Gemma 3 model with 270M parameters, fine-tuned for instruction following",
            "labels": ["phishing", "spam", "benign"]
        },
        "model_info": {
            "parameters": "270M",
            "architecture": "Transformer",
            "provider": "Google/HuggingFace"
        }
    }

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
