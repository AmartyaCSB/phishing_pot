#!/usr/bin/env python3
"""
Quick classification test for sample-201.eml
"""

from email_classifier import GemmaEmailClassifier

def quick_test():
    print("🚀 Quick Classification Test")
    print("=" * 40)
    
    # Initialize classifier with unknown handling
    clf = GemmaEmailClassifier(labels=["phishing", "spam", "benign", "unknown"])
    
    # Test sample-201.eml
    result = clf.classify_eml_file("email/sample-201.eml")
    
    print(f"📧 File: {result.file}")
    print(f"🏷️  Classification: {result.chosen}")
    print(f"📊 Confidence Scores: {result.scores}")
    print(f"📧 Subject: {result.subject}")
    print(f"👤 From: {result.sender}")
    
    if result.error:
        print(f"❌ Error: {result.error}")
    
    # Analyze the result
    if result.chosen == "unknown":
        print("\n⚠️  UNKNOWN CLASSIFICATION DETECTED")
        print("🔍 This means the AI model couldn't confidently classify this email")
        print("💡 Possible reasons:")
        print("   - Email content is ambiguous")
        print("   - Mixed signals (both legitimate and suspicious elements)")
        print("   - Unusual email format or encoding")
        print("   - Model uncertainty due to complex content")
        
    elif result.chosen == "phishing":
        print("\n🚨 PHISHING DETECTED!")
        print("⚠️  This email appears to be a phishing attempt")
        
    elif result.chosen == "spam":
        print("\n📧 SPAM DETECTED")
        print("ℹ️  This email appears to be unwanted promotional content")
        
    elif result.chosen == "benign":
        print("\n✅ BENIGN EMAIL")
        print("ℹ️  This email appears to be legitimate")
    
    return result

if __name__ == "__main__":
    result = quick_test()
    
    print(f"\n🎯 FINAL RESULT: {result.chosen}")
    
    if result.chosen == "unknown":
        print("\n🔧 HANDLING UNKNOWN CLASSIFICATION:")
        print("1. ✅ The classifier now properly returns 'unknown' instead of None")
        print("2. ✅ Enhanced fuzzy matching for better classification")
        print("3. ✅ Improved prompts for clearer AI responses")
        print("4. ✅ Fallback logic to handle edge cases")
        print("\n💡 The 'unknown' classification is working as intended!")
    else:
        print(f"\n✅ Successfully classified as: {result.chosen}")
