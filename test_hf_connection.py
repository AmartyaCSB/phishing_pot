#!/usr/bin/env python3
"""
Test HuggingFace API connection and key validity
"""

import os
import requests
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip().strip('"\'')
                    os.environ[key] = value

def test_hf_connection():
    """Test HuggingFace API connection"""
    print("🔍 Testing HuggingFace API Connection...")
    
    # Load environment
    load_env_file()
    
    # Get API key
    hf_key = os.getenv("HF_API_KEY") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
    
    if not hf_key:
        print("❌ No HuggingFace API key found!")
        return False
    
    print(f"✅ API key found: {hf_key[:10]}...")
    
    # Test basic API access
    try:
        print("🌐 Testing basic HuggingFace API access...")
        headers = {"Authorization": f"Bearer {hf_key}"}
        
        # Test with a simple API call
        response = requests.get(
            "https://huggingface.co/api/whoami",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ API key is valid! User: {user_info.get('name', 'Unknown')}")
        else:
            print(f"❌ API key validation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    
    # Test model access
    try:
        print("🤖 Testing Gemma model access...")
        model_url = "https://huggingface.co/api/models/google/gemma-3-270m-it"
        
        response = requests.get(model_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Gemma model is accessible!")
        else:
            print(f"⚠️  Model access issue: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Model access error: {e}")
    
    # Test transformers library
    try:
        print("📚 Testing transformers library...")
        import transformers
        print(f"✅ Transformers version: {transformers.__version__}")
        
        # Test HuggingFace login
        from huggingface_hub import login
        login(token=hf_key)
        print("✅ HuggingFace login successful!")
        
    except Exception as e:
        print(f"❌ Transformers/login error: {e}")
        return False
    
    return True

def test_alternative_approach():
    """Test alternative model loading approach"""
    print("\n🔄 Testing alternative model loading...")
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        
        print("📥 Attempting to load tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            "google/gemma-3-270m-it",
            trust_remote_code=True
        )
        print("✅ Tokenizer loaded successfully!")
        
        print("📥 Attempting to load model...")
        model = AutoModelForCausalLM.from_pretrained(
            "google/gemma-3-270m-it",
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        print("✅ Model loaded successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Alternative loading failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 HuggingFace Connection Test")
    print("=" * 50)
    
    # Test connection
    connection_ok = test_hf_connection()
    
    if connection_ok:
        print("\n" + "=" * 50)
        test_alternative_approach()
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")
