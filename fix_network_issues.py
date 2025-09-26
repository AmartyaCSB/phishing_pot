#!/usr/bin/env python3
"""
Fix network connectivity issues with HuggingFace
"""

import os
import ssl
import certifi
import requests
from pathlib import Path

def fix_ssl_issues():
    """Fix SSL/TLS connectivity issues"""
    print("🔧 Fixing SSL/TLS Issues...")
    
    # Set SSL certificate path
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
    
    # Disable SSL verification for testing (not recommended for production)
    os.environ['CURL_CA_BUNDLE'] = ''
    
    print("✅ SSL environment variables set")

def test_connectivity():
    """Test basic connectivity to HuggingFace"""
    print("🌐 Testing connectivity...")
    
    try:
        # Test basic HTTP connectivity
        response = requests.get("https://httpbin.org/get", timeout=10)
        print("✅ Basic internet connectivity: OK")
    except Exception as e:
        print(f"❌ Basic connectivity failed: {e}")
        return False
    
    try:
        # Test HuggingFace connectivity
        response = requests.get("https://huggingface.co", timeout=10)
        print("✅ HuggingFace website accessible: OK")
    except Exception as e:
        print(f"❌ HuggingFace connectivity failed: {e}")
        return False
    
    return True

def setup_offline_mode():
    """Setup for offline/local model usage"""
    print("📦 Setting up offline mode...")
    
    # Set HuggingFace to offline mode
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    
    print("✅ Offline mode enabled")

def create_simple_classifier():
    """Create a simple rule-based classifier as fallback"""
    print("🔄 Creating fallback classifier...")
    
    fallback_code = '''
import re
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class SimpleResult:
    file: str
    chosen: str
    scores: List[tuple]
    subject: str = ""
    sender: str = ""
    recipient: str = ""
    error: str = None

class SimpleFallbackClassifier:
    """Simple rule-based classifier for when AI model is unavailable"""
    
    def __init__(self):
        self.phishing_keywords = [
            'verify account', 'click here', 'urgent', 'suspended', 'confirm identity',
            'update payment', 'security alert', 'pending transaction', 'withdrawal',
            'bitcoin', 'crypto', 'trustwallet', 'banco', 'bradesco', 'livelo'
        ]
        
        self.spam_keywords = [
            'unsubscribe', 'marketing', 'promotion', 'offer', 'discount', 
            'sale', 'newsletter', 'deal', 'free', 'limited time'
        ]
    
    def classify_eml_file(self, filepath: str) -> SimpleResult:
        """Classify email using simple rules"""
        try:
            with open(filepath, 'rb') as f:
                content = f.read().decode('utf-8', errors='ignore')
            
            content_lower = content.lower()
            
            # Extract basic info
            subject = self._extract_header(content, 'Subject:')
            sender = self._extract_header(content, 'From:')
            recipient = self._extract_header(content, 'To:')
            
            # Count keyword matches
            phishing_score = sum(1 for keyword in self.phishing_keywords if keyword in content_lower)
            spam_score = sum(1 for keyword in self.spam_keywords if keyword in content_lower)
            
            # Determine classification
            if phishing_score > 0:
                classification = "phishing"
                confidence = min(0.8, 0.5 + (phishing_score * 0.1))
            elif spam_score > 0:
                classification = "spam" 
                confidence = min(0.7, 0.4 + (spam_score * 0.1))
            else:
                classification = "benign"
                confidence = 0.6
            
            scores = [
                (classification, confidence),
                ("unknown", 1.0 - confidence)
            ]
            
            return SimpleResult(
                file=filepath,
                chosen=classification,
                scores=scores,
                subject=subject,
                sender=sender,
                recipient=recipient
            )
            
        except Exception as e:
            return SimpleResult(
                file=filepath,
                chosen="unknown",
                scores=[("unknown", 1.0)],
                error=str(e)
            )
    
    def _extract_header(self, content: str, header: str) -> str:
        """Extract email header value"""
        try:
            lines = content.split('\\n')
            for line in lines:
                if line.startswith(header):
                    return line.split(':', 1)[1].strip()
        except:
            pass
        return ""

# Test the fallback classifier
if __name__ == "__main__":
    classifier = SimpleFallbackClassifier()
    result = classifier.classify_eml_file("email/sample-201.eml")
    print(f"Classification: {result.chosen}")
    print(f"Scores: {result.scores}")
    print(f"Subject: {result.subject}")
'''
    
    with open('fallback_classifier.py', 'w') as f:
        f.write(fallback_code)
    
    print("✅ Fallback classifier created: fallback_classifier.py")

def main():
    """Main troubleshooting function"""
    print("🚀 HuggingFace Connectivity Troubleshooter")
    print("=" * 50)
    
    # Step 1: Fix SSL issues
    fix_ssl_issues()
    
    # Step 2: Test connectivity
    if not test_connectivity():
        print("\n❌ Network connectivity issues detected")
        print("🔄 Setting up offline mode and fallback...")
        setup_offline_mode()
        create_simple_classifier()
        
        print("\n💡 SOLUTIONS:")
        print("1. Use the fallback classifier: python fallback_classifier.py")
        print("2. Check your firewall/antivirus settings")
        print("3. Try using a VPN if corporate network blocks HuggingFace")
        print("4. Wait and retry - HuggingFace servers might be temporarily down")
        
        return False
    
    print("\n✅ Network connectivity is OK")
    print("💡 The TLS error might be temporary. Try running your classifier again.")
    
    return True

if __name__ == "__main__":
    main()
