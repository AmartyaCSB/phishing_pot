#!/usr/bin/env python3
"""
Test script to classify sample-201.eml and handle unknown results
"""

import os
from pathlib import Path
from email_classifier import GemmaEmailClassifier

def test_sample_201():
    """Test classification of sample-201.eml"""
    print("🧪 Testing sample-201.eml Classification")
    print("=" * 50)
    
    # Check if file exists
    sample_file = Path("email/sample-201.eml")
    if not sample_file.exists():
        print(f"❌ File not found: {sample_file}")
        return False
    
    print(f"📧 Found file: {sample_file}")
    print(f"📏 File size: {sample_file.stat().st_size} bytes")
    
    # Initialize classifier with updated labels including "unknown"
    print("\n🤖 Initializing classifier...")
    try:
        clf = GemmaEmailClassifier(labels=["phishing", "spam", "benign", "unknown"])
        print("✅ Classifier initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize classifier: {e}")
        return False
    
    # Classify the email
    print(f"\n🔍 Classifying {sample_file.name}...")
    try:
        result = clf.classify_eml_file(str(sample_file))
        
        print(f"\n📊 CLASSIFICATION RESULTS:")
        print(f"File: {result.file}")
        print(f"Classification: {result.chosen}")
        print(f"Subject: {result.subject}")
        print(f"From: {result.sender}")
        print(f"To: {result.recipient}")
        print(f"Scores: {result.scores}")
        
        if result.error:
            print(f"❌ Error: {result.error}")
        
        if result.raw_model_output:
            print(f"\n🤖 Raw model output:")
            print(result.raw_model_output[:200] + "..." if len(result.raw_model_output) > 200 else result.raw_model_output)
        
        # Handle different classification results
        print(f"\n🎯 RESULT ANALYSIS:")
        
        if result.chosen == "unknown" or result.chosen is None:
            print("⚠️  Classification returned UNKNOWN")
            print("🔄 Attempting enhanced classification...")
            
            # Try with more explicit prompting
            enhanced_result = classify_with_enhanced_prompt(clf, str(sample_file))
            if enhanced_result:
                print(f"✅ Enhanced classification: {enhanced_result}")
            else:
                print("❌ Enhanced classification also failed")
                
        elif result.chosen == "phishing":
            print("🚨 PHISHING EMAIL DETECTED!")
            print("⚠️  This email appears to be a phishing attempt")
            
        elif result.chosen == "spam":
            print("📧 SPAM EMAIL DETECTED")
            print("ℹ️  This email appears to be spam/promotional content")
            
        elif result.chosen == "benign":
            print("✅ BENIGN EMAIL")
            print("ℹ️  This email appears to be legitimate")
        
        return True
        
    except Exception as e:
        print(f"❌ Classification failed: {e}")
        return False

def classify_with_enhanced_prompt(classifier, filepath):
    """Try classification with enhanced prompting for unknown cases"""
    try:
        # Read the email content directly
        with open(filepath, 'rb') as f:
            email_content = f.read()
        
        # Extract text using the classifier's method
        from email import policy
        from email.parser import BytesParser
        
        msg = BytesParser(policy=policy.default).parsebytes(email_content)
        text_content = classifier._extract_text(msg)
        
        # Create enhanced prompt for unclear cases
        enhanced_labels = ["phishing", "spam", "benign"]
        
        # Use a more detailed analysis
        print("🔍 Analyzing email content for suspicious patterns...")
        
        # Check for common phishing indicators
        suspicious_patterns = [
            "verify account", "click here", "urgent", "suspended", 
            "confirm identity", "update payment", "security alert",
            "pending transaction", "withdrawal", "bitcoin", "crypto"
        ]
        
        content_lower = text_content.lower()
        found_patterns = [pattern for pattern in suspicious_patterns if pattern in content_lower]
        
        if found_patterns:
            print(f"🚨 Found suspicious patterns: {found_patterns}")
            return "phishing"
        
        # Check for spam indicators
        spam_patterns = [
            "unsubscribe", "marketing", "promotion", "offer", 
            "discount", "sale", "newsletter"
        ]
        
        found_spam = [pattern for pattern in spam_patterns if pattern in content_lower]
        
        if found_spam:
            print(f"📧 Found spam patterns: {found_spam}")
            return "spam"
        
        # If no clear patterns, try the model again with simpler prompt
        try:
            chosen, scores, raw_output = classifier.classify_text(text_content[:1000])  # Limit text length
            if chosen and chosen != "unknown":
                return chosen
        except Exception:
            pass
        
        return None
        
    except Exception as e:
        print(f"❌ Enhanced classification error: {e}")
        return None

def analyze_email_content(filepath):
    """Analyze the actual email content to understand why it might be unknown"""
    print(f"\n📖 CONTENT ANALYSIS:")
    
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        
        # Parse email
        from email import policy
        from email.parser import BytesParser
        
        msg = BytesParser(policy=policy.default).parsebytes(content)
        
        # Extract key information
        subject = msg.get("Subject", "")
        sender = msg.get("From", "")
        
        print(f"Subject: {subject}")
        print(f"From: {sender}")
        
        # Get text content
        clf = GemmaEmailClassifier()
        text_content = clf._extract_text(msg)
        
        print(f"Content length: {len(text_content)} characters")
        print(f"First 300 characters:")
        print(text_content[:300])
        
        return text_content
        
    except Exception as e:
        print(f"❌ Content analysis error: {e}")
        return None

if __name__ == "__main__":
    # Test the classification
    success = test_sample_201()
    
    if success:
        print("\n📋 Additional content analysis...")
        analyze_email_content("email/sample-201.eml")
    
    print(f"\n🏁 Test completed!")
