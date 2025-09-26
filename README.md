# 🛡️ Email Classification API

**AI-Powered Email Classification Service using Google's Gemma-3-270m-it Model**

This is a production-ready FastAPI microservice that automatically classifies emails as **phishing**, **spam**, or **benign** using Google's advanced Gemma AI model. The service is designed for cybersecurity professionals, researchers, and developers who need to analyze email content for security threats.

## 🎯 What This Service Does

This email classification service provides:

- **Automated Threat Detection**: Identifies phishing attempts, spam, and legitimate emails
- **Real-time Analysis**: Processes .eml email files and returns instant classification results
- **High Accuracy**: Uses Google's Gemma-3-270m-it model (270 million parameters) for reliable detection
- **Easy Integration**: RESTful API that can be integrated into existing security systems
- **Web Interface**: User-friendly drag-and-drop interface for manual email analysis

## 🚀 Key Features

- **🤖 AI-Powered Classification**: Uses Google's Gemma-3-270m-it model for accurate email analysis
- **🌐 FastAPI Backend**: Modern, fast web API with automatic interactive documentation
- **📧 File Upload Support**: Upload .eml files through web interface or API endpoints
- **📊 Batch Processing**: Classify multiple emails simultaneously for efficiency
- **💾 Smart Caching**: Intelligent caching system for improved performance and reduced API calls
- **🔒 Security Focused**: Built specifically for cybersecurity and threat detection use cases

## 🏗️ Architecture & Components

### **Core Components Explained:**

**📁 `email_classifier.py`** - **AI Classification Engine**
- Contains the `GemmaEmailClassifier` class that interfaces with Google's Gemma model
- Handles email parsing from .eml format (extracts headers, body, attachments)
- Processes text content and sends it to the AI model for classification
- Parses model responses and returns structured classification results
- **Why it exists**: This is the core AI component that does the actual email analysis

**📁 `classifier_service.py`** - **Service Layer & Performance Optimization**
- Wraps the email classifier with additional enterprise features
- Implements intelligent caching to avoid re-processing identical emails
- Provides batch processing capabilities for multiple emails
- Handles error management and performance monitoring
- Manages model lifecycle and memory usage
- **Why it exists**: Adds production-ready features like caching, error handling, and performance optimization

**📁 `app.py`** - **FastAPI Web Server & API Endpoints**
- Creates the web server using FastAPI framework
- Defines all REST API endpoints for email classification
- Provides a web interface for drag-and-drop file uploads
- Handles HTTP requests, file validation, and response formatting
- Includes CORS support for web integration
- **Why it exists**: Makes the classification service accessible via web API and provides a user interface

**📁 `run.py`** - **Simple Startup Script**
- Loads environment variables from .env file
- Starts the FastAPI server with basic configuration
- **Why it exists**: Provides an easy way to start the service locally

**📁 `start_server.py`** - **Advanced Startup with Diagnostics**
- Performs comprehensive system checks before starting
- Validates HuggingFace API key and dependencies
- Provides detailed logging and error messages
- **Why it exists**: Helps troubleshoot setup issues and provides better feedback

### **Project Structure:**
```
├── app.py                 # FastAPI web server & API endpoints
├── classifier_service.py  # Service layer with caching & batch processing
├── email_classifier.py    # Core AI classification engine
├── run.py                 # Simple server startup
├── start_server.py        # Advanced startup with diagnostics
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
└── email/                 # Sample email files for testing (5946 .eml files)
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/AmartyaCSB/phishing_pot.git
cd phishing_pot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Get Your HuggingFace API Key (Required)

**⚠️ Important**: You need your own HuggingFace API key to use this service.

**Step-by-step instructions:**

1. **Create HuggingFace Account**
   - Go to [HuggingFace.co](https://huggingface.co)
   - Sign up for a free account (no payment required)

2. **Generate API Token**
   - After logging in, go to your profile → Settings → Access Tokens
   - Click "New token"
   - Give it a name (e.g., "email-classifier")
   - Select "Read" permissions (sufficient for this service)
   - Click "Generate"
   - Copy the token (starts with `hf_...`)

3. **Configure the Service**
   ```bash
   # Create your environment file
   cp .env.example .env
   
   # Edit .env file and add your key:
   HF_API_KEY="hf_your_actual_key_here"
   ```

**Why do you need this?**
- The service uses Google's Gemma-3-270m-it model hosted on HuggingFace
- The API key allows the service to download and use the AI model
- It's free for the usage levels of this service
- Your key remains private and is only stored locally in your .env file

### 4. Start the FastAPI Server

**Option 1: Simple startup (Recommended)**
```bash
python run.py
```

**Option 2: Full startup with diagnostics**
```bash
python start_server.py
```

The server will start and show:
```
🚀 Starting Email Classification API Server...
🔍 Checking requirements...
📧 Found 5946 .eml files in email directory
✅ HuggingFace API key found
✅ All required packages are available
🌐 Server will start on http://0.0.0.0:8000
📚 API Documentation: http://0.0.0.0:8000/docs
INFO: Uvicorn running on http://0.0.0.0:8000
```

### 5. Access the Service

- **🌐 Web Interface**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs

### 6. Test the Classification

**Via Web Interface:**
1. Open http://localhost:8000 in your browser
2. Drag and drop any `.eml` file
3. Click "Classify Email" to see results

**Via API:**
```bash
# Upload and classify an email
curl -X POST "http://localhost:8000/classify/upload" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@email/sample-1.eml"
```

## 📡 API Endpoints & Usage

The service provides a RESTful API with the following endpoints:

### **Available Endpoints:**

| Method | Endpoint | Purpose | Description |
|--------|----------|---------|-------------|
| `GET` | `/` | **Web Interface** | User-friendly drag-and-drop interface for manual email analysis |
| `POST` | `/classify/upload` | **Single Classification** | Upload one .eml file and get classification result |
| `POST` | `/classify/batch` | **Batch Processing** | Upload multiple .eml files for simultaneous classification |
| `GET` | `/docs` | **API Documentation** | Interactive Swagger UI documentation with live testing |

### **Why These Endpoints Exist:**

**🌐 Web Interface (`GET /`)**
- **Purpose**: Provides a user-friendly way to test the service manually
- **Use case**: Security analysts can quickly drag-and-drop suspicious emails for analysis
- **Features**: Real-time results, confidence scores, email metadata display

**📧 Single Classification (`POST /classify/upload`)**
- **Purpose**: Core API endpoint for integrating into other systems
- **Use case**: Security tools can send individual emails for real-time threat detection
- **Response**: Detailed classification with confidence scores and processing time

**📊 Batch Processing (`POST /classify/batch`)**
- **Purpose**: Efficient processing of multiple emails simultaneously
- **Use case**: Bulk analysis of email archives or incoming email queues
- **Benefits**: Reduces API calls and improves throughput for large datasets

**📚 API Documentation (`GET /docs`)**
- **Purpose**: Interactive documentation for developers
- **Features**: Live API testing, request/response examples, schema definitions
- **Benefits**: Developers can test endpoints directly from the browser

### **API Usage Examples:**

**Single File Classification:**
```bash
curl -X POST "http://localhost:8000/classify/upload" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@suspicious_email.eml"
```

**Batch Classification:**
```bash
curl -X POST "http://localhost:8000/classify/batch" \
     -H "Content-Type: multipart/form-data" \
     -F "files=@email1.eml" \
     -F "files=@email2.eml" \
     -F "files=@email3.eml"
```

**Windows PowerShell Examples:**
```powershell
# Single file
Invoke-RestMethod -Uri "http://localhost:8000/classify/upload" -Method Post -Form @{file=Get-Item "email/sample-1.eml"}

# Multiple files (batch)
$files = Get-ChildItem "email/sample-*.eml" | Select-Object -First 3
$form = @{}
foreach ($file in $files) { $form["files"] = $file }
Invoke-RestMethod -Uri "http://localhost:8000/classify/batch" -Method Post -Form $form
```

## 📊 Response Format

```json
{
  "file_name": "sample.eml",
  "classification": "phishing",
  "confidence_scores": [
    {"label": "phishing", "score": 0.85},
    {"label": "spam", "score": 0.12},
    {"label": "benign", "score": 0.03}
  ],
  "metadata": {
    "subject": "Urgent: Verify Your Account",
    "sender": "noreply@suspicious-bank.com",
    "recipient": "user@example.com"
  },
  "processing_time_ms": 150,
  "model_version": "google/gemma-3-270m-it"
}
```

## 🧪 Testing the Service

### **Testing Methods:**

**1. Web Interface Testing (Easiest)**
1. Open http://localhost:8000 in your browser
2. Drag and drop any `.eml` file from the `email/` directory
3. Click "Classify Email" to see results instantly
4. View detailed results including confidence scores and email metadata

**2. API Testing**
```bash
# Windows PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/classify/upload" -Method Post -Form @{file=Get-Item "email/sample-1.eml"}

# Expected response:
# {"file_name": "sample-1.eml", "classification": "phishing", ...}
```

**3. Interactive API Documentation**
1. Open http://localhost:8000/docs in your browser
2. Use the Swagger UI to test endpoints directly
3. Upload files and see live responses
4. Explore all available endpoints and their parameters

**4. Batch Processing Testing**
```bash
# Python test script
python test_batch_api.py

# PowerShell test script (Windows)
.\test_batch_powershell.ps1

# Bash/curl test script (Cross-platform)
bash test_batch_curl.sh
```

### **Sample Test Files:**
The `email/` directory contains 5946 real email samples for testing:
- **Phishing emails**: Banking scams, cryptocurrency fraud, account verification attempts
- **Spam emails**: Marketing content, promotional emails
- **Benign emails**: Legitimate business communications

### **Expected Results:**
- **Processing time**: 100-500ms per email after model loading
- **Classification accuracy**: ~85-95% for phishing detection
- **Response format**: JSON with classification, confidence scores, and metadata

## 🔧 Troubleshooting

**API Key Issues:**
```bash
# Make sure your .env file contains:
HF_API_KEY="hf_your_actual_key_here"

# Restart the server after updating .env
```

**Model Loading:**
- First startup takes ~30 seconds to download the model
- Requires ~2-4GB RAM and stable internet connection
- Model is cached locally after first download
- Classification speed: ~100-500ms per email after loading

**Port Issues:**
```bash
# If port 8000 is busy, edit .env:
API_PORT=8001

# Or check what's using the port:
netstat -an | findstr :8000
```

**Environment Setup:**
```bash
# Activate conda environment (if using conda)
conda activate your-env-name

# Verify dependencies
python -c "import torch, transformers, fastapi; print('✅ All dependencies OK')"
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**⚠️ Disclaimer**: This tool is for educational and research purposes only.

