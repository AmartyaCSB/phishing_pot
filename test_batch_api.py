#!/usr/bin/env python3
"""
Test script for batch email classification API
"""

import os
import time
import requests
import json
from pathlib import Path

def test_single_file_api():
    """Test single file upload API"""
    print("🧪 Testing Single File API")
    print("-" * 40)
    
    sample_file = Path("email/sample-201.eml")
    if not sample_file.exists():
        print(f"❌ Sample file not found: {sample_file}")
        return False
    
    try:
        with open(sample_file, 'rb') as f:
            files = {'file': (sample_file.name, f, 'application/octet-stream')}
            
            print(f"📤 Uploading: {sample_file.name}")
            start_time = time.time()
            
            response = requests.post(
                "http://localhost:8000/classify/upload",
                files=files,
                timeout=60
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! ({elapsed:.2f}s)")
                print(f"🏷️  Classification: {data.get('classification', 'N/A')}")
                print(f"📊 Confidence: {data.get('confidence_scores', [{}])[0].get('score', 0):.2f}")
                print(f"⏱️  Processing Time: {data.get('processing_time_ms', 0)}ms")
                return True
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_batch_api():
    """Test batch file upload API"""
    print("\n🧪 Testing Batch API")
    print("-" * 40)
    
    # Get multiple sample files
    email_dir = Path("email")
    sample_files = list(email_dir.glob("sample-*.eml"))[:5]  # Test with 5 files
    
    if len(sample_files) < 2:
        print("❌ Need at least 2 sample files for batch testing")
        return False
    
    print(f"📧 Selected {len(sample_files)} files for batch testing:")
    for f in sample_files:
        print(f"   • {f.name}")
    
    try:
        files = []
        for sample_file in sample_files:
            with open(sample_file, 'rb') as f:
                files.append(('files', (sample_file.name, f.read(), 'application/octet-stream')))
        
        print(f"\n📤 Uploading batch of {len(files)} files...")
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:8000/classify/batch",
            files=files,
            timeout=120
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Batch processing successful! ({elapsed:.2f}s)")
            
            print(f"\n📊 BATCH SUMMARY:")
            print(f"   • Total Files: {data.get('total_files', 0)}")
            print(f"   • Successful: {data.get('successful_classifications', 0)}")
            print(f"   • Failed: {data.get('failed_classifications', 0)}")
            print(f"   • Total Processing Time: {data.get('total_processing_time_ms', 0):.0f}ms")
            
            avg_time = data.get('total_processing_time_ms', 0) / max(1, data.get('total_files', 1))
            print(f"   • Average Time per File: {avg_time:.0f}ms")
            
            print(f"\n📋 INDIVIDUAL RESULTS:")
            for i, result in enumerate(data.get('results', []), 1):
                classification = result.get('classification', 'unknown')
                confidence = result.get('confidence_scores', [{}])[0].get('score', 0)
                processing_time = result.get('processing_time_ms', 0)
                
                print(f"   {i}. {result.get('file_name', 'Unknown')}")
                print(f"      🏷️  {classification} ({confidence:.2f} confidence)")
                print(f"      ⏱️  {processing_time}ms")
                
                if result.get('error'):
                    print(f"      ❌ Error: {result['error']}")
            
            return True
        else:
            print(f"❌ Batch processing failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_api_endpoints():
    """Test various API endpoints"""
    print("\n🧪 Testing API Endpoints")
    print("-" * 40)
    
    endpoints = [
        ("GET", "/", "Web Interface"),
        ("GET", "/docs", "API Documentation"),
        ("GET", "/models", "Model Information")
    ]
    
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"http://localhost:8000{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {description}: OK")
            else:
                print(f"❌ {description}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {description}: Error - {e}")

def test_error_handling():
    """Test error handling with invalid files"""
    print("\n🧪 Testing Error Handling")
    print("-" * 40)
    
    # Test with non-EML file
    try:
        test_content = b"This is not an EML file"
        files = {'file': ('test.txt', test_content, 'text/plain')}
        
        response = requests.post(
            "http://localhost:8000/classify/upload",
            files=files,
            timeout=30
        )
        
        if response.status_code == 400:
            print("✅ Correctly rejected non-EML file")
        else:
            print(f"⚠️  Unexpected response for invalid file: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing invalid file: {e}")
    
    # Test with oversized file (if we had one)
    print("✅ Error handling tests completed")

def test_performance():
    """Test performance with multiple concurrent requests"""
    print("\n🧪 Testing Performance")
    print("-" * 40)
    
    sample_file = Path("email/sample-201.eml")
    if not sample_file.exists():
        print("❌ Sample file not found for performance testing")
        return
    
    # Test sequential requests
    print("📊 Testing sequential requests...")
    times = []
    
    for i in range(3):
        try:
            with open(sample_file, 'rb') as f:
                files = {'file': (sample_file.name, f, 'application/octet-stream')}
                
                start_time = time.time()
                response = requests.post(
                    "http://localhost:8000/classify/upload",
                    files=files,
                    timeout=60
                )
                elapsed = time.time() - start_time
                
                if response.status_code == 200:
                    times.append(elapsed)
                    print(f"   Request {i+1}: {elapsed:.2f}s")
                else:
                    print(f"   Request {i+1}: Failed ({response.status_code})")
                    
        except Exception as e:
            print(f"   Request {i+1}: Error - {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"📈 Average response time: {avg_time:.2f}s")
        print(f"📈 Min/Max: {min(times):.2f}s / {max(times):.2f}s")

def main():
    """Main test function"""
    print("🚀 Email Classification API - Batch Testing")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print("✅ Server is running")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        print("💡 Make sure to start the server first: python run.py")
        return False
    
    # Run tests
    tests = [
        ("Single File API", test_single_file_api),
        ("Batch API", test_batch_api),
        ("API Endpoints", test_api_endpoints),
        ("Error Handling", test_error_handling),
        ("Performance", test_performance)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    passed = 0
    for test_name, result in results:
        if result is not None:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
            if result:
                passed += 1
        else:
            print(f"ℹ️  INFO - {test_name}")
    
    print(f"\nResults: {passed}/{len([r for r in results if r[1] is not None])} tests passed")
    
    if passed > 0:
        print("\n🎉 Batch API testing completed!")
        print("\n💡 Usage Examples:")
        print("   • Single file: POST /classify/upload")
        print("   • Multiple files: POST /classify/batch")
        print("   • Web interface: http://localhost:8000")
    
    return True

if __name__ == "__main__":
    main()
