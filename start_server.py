#!/usr/bin/env python3
"""
Email Classification System - Server Startup Script
"""

import os
import sys
from pathlib import Path

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("💡 Create .env file with your HuggingFace API key:")
        print("   HF_API_KEY=your_api_key_here")
        print("   HUGGINGFACEHUB_API_TOKEN=your_api_key_here")
        return False
    
    # Load and check API key
    with open(env_file, 'r') as f:
        env_content = f.read()
        if 'HF_API_KEY=' in env_content or 'HUGGINGFACEHUB_API_TOKEN=' in env_content:
            print("✅ API key configuration found")
        else:
            print("❌ No API key found in .env file")
            return False
    
    # Check required files
    required_files = [
        "working_api.py",
        "email_classifier.py", 
        "frontend.html",
        "requirements.txt"
    ]
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} missing")
            return False
    
    return True

def load_environment():
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

def main():
    """Main startup function"""
    print("🚀 Email Classification System")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed")
        print("💡 Please fix the issues above and try again")
        return
    
    print("\n✅ Environment check passed")
    
    # Load environment variables
    load_environment()
    
    print("\n🌐 Starting server...")
    print("📍 Web Interface: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("\n⏳ Loading AI model (this may take a moment)...")
    
    # Start the server
    try:
        import uvicorn
        uvicorn.run(
            "working_api:app",
            host="127.0.0.1",
            port=8000,
            reload=False,
            log_level="info"
        )
    except ImportError:
        print("❌ uvicorn not installed")
        print("💡 Install dependencies: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")

if __name__ == "__main__":
    main()
