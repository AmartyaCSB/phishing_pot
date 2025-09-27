# 🛡️ Email Classification System - Setup Guide

A complete AI-powered email security analysis tool with a beautiful web interface.

## 🚀 Quick Setup (5 minutes)

### 1. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Configure API Key**
```bash
# Copy the environment template
cp .env.example .env

# Edit .env and add your HuggingFace API key
# Get your key from: https://huggingface.co/settings/tokens
```

Your `.env` file should look like:
```env
HF_API_KEY=hf_your_actual_api_key_here
HUGGINGFACEHUB_API_TOKEN=hf_your_actual_api_key_here
```

### 3. **Start the Server**
```bash
python start_server.py
```

### 4. **Open Web Interface**
Navigate to: **http://localhost:8000**

## 📋 Core Files

| File | Purpose |
|------|---------|
| `start_server.py` | 🚀 Main startup script |
| `working_api.py` | 🔧 FastAPI backend server |
| `email_classifier.py` | 🤖 AI classification engine |
| `frontend.html` | 🌐 Beautiful web interface |
| `classify_all_emails.py` | 📊 Batch CSV processing |
| `requirements.txt` | 📦 Python dependencies |
| `.env.example` | ⚙️ Environment template |

## 💻 Usage Options

### Option 1: Web Interface (Recommended)
1. Open http://localhost:8000
2. Drag & drop .eml files
3. Click "Classify X Emails"
4. View beautiful results

### Option 2: API Integration
```bash
# Classify multiple emails
curl -X POST "http://localhost:8000/classify/batch" \
     -F "files=@email1.eml" -F "files=@email2.eml"

# Single email
curl -X POST "http://localhost:8000/classify/email" \
     -F "file=@email.eml"
```

### Option 3: CSV Export
```bash
# Process all emails in /email directory to CSV
python classify_all_emails.py
```

## 🔧 Troubleshooting

### "Classifier not loaded"
- Check your HuggingFace API key in `.env`
- Ensure you have internet connection
- Verify Python 3.8+ is installed

### "Port 8000 already in use"
- Kill existing processes: `taskkill /F /IM python.exe`
- Or change port in `start_server.py`

### "Out of memory"
- Ensure 4GB+ RAM available
- Close other applications
- Process smaller batches

## 📊 Classification Results

The AI classifies emails into:
- 🔴 **Phishing** - Malicious fraud attempts
- 🟠 **Spam** - Unwanted promotional emails
- 🟢 **Benign** - Legitimate, safe emails

Each result includes:
- Confidence score (0-100%)
- Email metadata (subject, sender, recipient)
- Processing time

## 🎯 Perfect For

- **Cybersecurity professionals** analyzing threats
- **IT administrators** screening emails
- **Researchers** studying phishing patterns
- **Security teams** bulk-processing samples

---

**Need help?** Check the full documentation in `README_CLASSIFICATION.md`

**Ready to start?** Run `python start_server.py` and open http://localhost:8000
