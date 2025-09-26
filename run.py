#!/usr/bin/env python3
"""
Simple startup script that loads .env file and starts the server
"""

import os
import sys
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path(".env")
    if env_file.exists():
        print("📄 Loading environment variables from .env file...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip().strip('"\'')
                    os.environ[key] = value
                    if key in ['HF_API_KEY', 'HUGGINGFACEHUB_API_TOKEN']:
                        print(f"✅ Loaded {key}")
    else:
        print("⚠️  No .env file found")

def main():
    """Main function"""
    print("🚀 Email Classification API - Simple Startup")
    print("=" * 50)
    
    # Load environment variables
    load_env_file()
    
    # Check for HuggingFace API key
    hf_key = os.getenv("HF_API_KEY") or os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if hf_key:
        print("✅ HuggingFace API key is configured")
    else:
        print("❌ No HuggingFace API key found!")
        print("💡 Please set HF_API_KEY in your .env file")
        return False
    
    # Start the server
    print("\n🌐 Starting server...")
    print("📍 Server will be available at:")
    print("   • Local access: http://localhost:8000")
    print("   • Network access: http://0.0.0.0:8000")
    print("   • API Documentation: http://localhost:8000/docs")
    print("\n🚀 Starting uvicorn server...")
    
    try:
        import uvicorn
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
