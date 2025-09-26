#!/usr/bin/env python3
"""
Enhanced Email Classifier Service
Wrapper around the existing email_classifier.py with additional features for microservice use
"""

import os
import time
import logging
from typing import Dict, List, Optional, Union
from dataclasses import asdict
from email_classifier import GemmaEmailClassifier, ClassificationResult

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailClassifierService:
    """
    Enhanced email classifier service with caching, error handling, and performance monitoring
    """
    
    def __init__(
        self,
        model_id: str = "google/gemma-3-270m-it",
        labels: Optional[List[str]] = None,
        hf_token: Optional[str] = None,
        cache_enabled: bool = True
    ):
        self.model_id = model_id
        self.labels = labels or ["phishing", "spam", "benign"]
        self.cache_enabled = cache_enabled
        self._classifier = None
        self._model_loaded = False
        self._classification_cache = {} if cache_enabled else None
        self._stats = {
            "total_classifications": 0,
            "cache_hits": 0,
            "errors": 0,
            "avg_processing_time": 0.0
        }
        
        # Initialize classifier
        self._load_model(hf_token)
    
    def _load_model(self, hf_token: Optional[str] = None):
        """Load the classification model"""
        try:
            logger.info(f"Loading model: {self.model_id}")
            start_time = time.time()
            
            self._classifier = GemmaEmailClassifier(
                model_id=self.model_id,
                labels=self.labels,
                hf_token=hf_token
            )
            
            load_time = time.time() - start_time
            self._model_loaded = True
            logger.info(f"Model loaded successfully in {load_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self._model_loaded = False
            raise
    
    def _get_file_hash(self, filepath: str) -> str:
        """Generate a simple hash for file caching"""
        import hashlib
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            return hashlib.md5(content).hexdigest()
        except Exception:
            return None
    
    def classify_file(self, filepath: str, use_cache: bool = True) -> Dict:
        """
        Classify a single email file
        
        Args:
            filepath: Path to the .eml file
            use_cache: Whether to use caching
            
        Returns:
            Dictionary with classification results
        """
        if not self._model_loaded:
            raise RuntimeError("Model not loaded. Cannot perform classification.")
        
        # Check cache
        file_hash = None
        if self.cache_enabled and use_cache:
            file_hash = self._get_file_hash(filepath)
            if file_hash and file_hash in self._classification_cache:
                self._stats["cache_hits"] += 1
                logger.info(f"Cache hit for file: {os.path.basename(filepath)}")
                return self._classification_cache[file_hash]
        
        try:
            start_time = time.time()
            
            # Perform classification
            result = self._classifier.classify_eml_file(filepath)
            processing_time = time.time() - start_time
            
            # Convert to dictionary format
            result_dict = {
                "file_name": os.path.basename(filepath),
                "classification": result.chosen,
                "confidence_scores": [
                    {"label": label, "score": score} 
                    for label, score in result.scores
                ],
                "metadata": {
                    "subject": result.subject,
                    "sender": result.sender,
                    "recipient": result.recipient,
                    "date": None  # Add date parsing if needed
                },
                "processing_time_ms": round(processing_time * 1000, 2),
                "model_version": self.model_id,
                "error": result.error,
                "raw_model_output": result.raw_model_output
            }
            
            # Update stats
            self._stats["total_classifications"] += 1
            if result.error:
                self._stats["errors"] += 1
            
            # Update average processing time
            total = self._stats["total_classifications"]
            current_avg = self._stats["avg_processing_time"]
            self._stats["avg_processing_time"] = (
                (current_avg * (total - 1) + processing_time) / total
            )
            
            # Cache result
            if self.cache_enabled and file_hash:
                self._classification_cache[file_hash] = result_dict
            
            logger.info(
                f"Classified {os.path.basename(filepath)}: "
                f"{result.chosen} ({processing_time:.2f}s)"
            )
            
            return result_dict
            
        except Exception as e:
            self._stats["errors"] += 1
            error_msg = f"Classification failed for {filepath}: {str(e)}"
            logger.error(error_msg)
            
            return {
                "file_name": os.path.basename(filepath),
                "classification": None,
                "confidence_scores": [],
                "metadata": {},
                "processing_time_ms": 0,
                "model_version": self.model_id,
                "error": error_msg,
                "raw_model_output": None
            }
    
    def classify_bytes(self, file_content: bytes, filename: str = "uploaded_file.eml") -> Dict:
        """
        Classify email from bytes content
        
        Args:
            file_content: Raw bytes of the .eml file
            filename: Name of the file for reference
            
        Returns:
            Dictionary with classification results
        """
        import tempfile
        
        # Write bytes to temporary file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.eml', delete=False) as tmp_file:
            tmp_file.write(file_content)
            tmp_path = tmp_file.name
        
        try:
            result = self.classify_file(tmp_path, use_cache=False)
            result["file_name"] = filename
            return result
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
    
    def classify_batch(self, filepaths: List[str]) -> List[Dict]:
        """
        Classify multiple email files
        
        Args:
            filepaths: List of paths to .eml files
            
        Returns:
            List of classification results
        """
        results = []
        total_files = len(filepaths)
        
        logger.info(f"Starting batch classification of {total_files} files")
        
        for i, filepath in enumerate(filepaths, 1):
            logger.info(f"Processing file {i}/{total_files}: {os.path.basename(filepath)}")
            result = self.classify_file(filepath)
            results.append(result)
        
        logger.info(f"Batch classification completed. Processed {len(results)} files")
        return results
    
    def get_stats(self) -> Dict:
        """Get service statistics"""
        return {
            **self._stats,
            "model_loaded": self._model_loaded,
            "model_id": self.model_id,
            "labels": self.labels,
            "cache_size": len(self._classification_cache) if self._classification_cache else 0
        }
    
    def clear_cache(self):
        """Clear the classification cache"""
        if self._classification_cache:
            self._classification_cache.clear()
            logger.info("Classification cache cleared")
    
    def health_check(self) -> Dict:
        """Perform health check"""
        return {
            "status": "healthy" if self._model_loaded else "unhealthy",
            "model_loaded": self._model_loaded,
            "model_id": self.model_id,
            "uptime_stats": self._stats
        }

# Global service instance (singleton pattern)
_service_instance = None

def get_classifier_service() -> EmailClassifierService:
    """Get the global classifier service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = EmailClassifierService()
    return _service_instance

# Test function
def test_service():
    """Test the classifier service"""
    service = get_classifier_service()
    
    # Test with a sample file
    email_dir = "email"
    if os.path.exists(email_dir):
        sample_files = [f for f in os.listdir(email_dir) if f.endswith('.eml')][:3]
        
        for filename in sample_files:
            filepath = os.path.join(email_dir, filename)
            result = service.classify_file(filepath)
            print(f"\n📧 File: {result['file_name']}")
            print(f"🏷️  Classification: {result['classification']}")
            print(f"📊 Confidence: {result['confidence_scores']}")
            print(f"⏱️  Time: {result['processing_time_ms']}ms")
    
    # Print stats
    stats = service.get_stats()
    print(f"\n📈 Service Stats: {stats}")

if __name__ == "__main__":
    test_service()
