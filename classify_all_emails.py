#!/usr/bin/env python3
"""
Simple script to classify all emails in the email folder and save to CSV
"""

import os
import csv
import time
from pathlib import Path
from email_classifier import GemmaEmailClassifier

def classify_all_emails():
    """Process all .eml files and create CSV with results"""
    
    print("🚀 Classifying All Emails to CSV")
    print("=" * 50)
    
    # Initialize classifier
    print("🤖 Loading classifier...")
    try:
        classifier = GemmaEmailClassifier()
        print("✅ Classifier loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load classifier: {e}")
        return False
    
    # Find all .eml files
    email_dir = Path("email")
    eml_files = list(email_dir.glob("*.eml"))
    total_files = len(eml_files)
    
    print(f"📧 Found {total_files} email files to process")
    
    if total_files == 0:
        print("❌ No .eml files found in email directory")
        return False
    
    # Create CSV file
    output_file = "email_classifications.csv"
    
    print(f"📄 Creating CSV file: {output_file}")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow([
            'filename',
            'classification', 
            'confidence',
            'subject',
            'sender',
            'recipient',
            'error'
        ])
        
        # Process each file
        successful = 0
        failed = 0
        start_time = time.time()
        
        for i, eml_file in enumerate(eml_files, 1):
            try:
                print(f"Processing {i}/{total_files}: {eml_file.name}", end=" ... ")
                
                # Classify the email
                result = classifier.classify_eml_file(str(eml_file))
                
                # Get confidence score (first score if available)
                confidence = result.scores[0][1] if result.scores else 0.0
                
                # Write to CSV
                writer.writerow([
                    eml_file.name,
                    result.chosen or 'unknown',
                    f"{confidence:.3f}",
                    (result.subject or '').replace('\n', ' ').replace('\r', ''),
                    (result.sender or '').replace('\n', ' ').replace('\r', ''),
                    (result.recipient or '').replace('\n', ' ').replace('\r', ''),
                    result.error or ''
                ])
                
                if result.error:
                    print(f"⚠️  {result.chosen} (error: {result.error[:50]}...)")
                    failed += 1
                else:
                    print(f"✅ {result.chosen} ({confidence:.3f})")
                    successful += 1
                
                # Show progress every 100 files
                if i % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = i / elapsed
                    remaining = (total_files - i) / rate
                    print(f"\n📊 Progress: {i}/{total_files} ({i/total_files*100:.1f}%)")
                    print(f"⏱️  Rate: {rate:.1f} files/sec, Est. remaining: {remaining:.0f}s")
                    print("-" * 50)
                
            except Exception as e:
                print(f"❌ Error: {str(e)[:50]}...")
                
                # Write error row
                writer.writerow([
                    eml_file.name,
                    'error',
                    '0.000',
                    '',
                    '',
                    '',
                    str(e)
                ])
                failed += 1
    
    # Final summary
    total_time = time.time() - start_time
    
    print(f"\n{'='*50}")
    print("🎉 PROCESSING COMPLETE!")
    print('='*50)
    print(f"📧 Total files: {total_files}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"⏱️  Total time: {total_time:.1f} seconds")
    print(f"📊 Average: {total_time/total_files:.2f} seconds per file")
    print(f"📄 Results saved to: {output_file}")
    
    # Show classification summary
    print(f"\n📊 Quick Summary:")
    classification_counts = {}
    
    with open(output_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            classification = row['classification']
            classification_counts[classification] = classification_counts.get(classification, 0) + 1
    
    for classification, count in sorted(classification_counts.items()):
        percentage = (count / total_files) * 100
        print(f"   • {classification}: {count} ({percentage:.1f}%)")
    
    return True

if __name__ == "__main__":
    classify_all_emails()
