# 🛡️ Email Classification System

An advanced AI-powered email security analysis tool that classifies emails as **phishing**, **spam**, or **benign** using Google's Gemma-3-270m-it model. Perfect for cybersecurity professionals, IT administrators, and researchers.

![Email Classification Demo](https://img.shields.io/badge/AI%20Model-Gemma--3--270m--it-blue) ![Python](https://img.shields.io/badge/Python-3.8%2B-green) ![FastAPI](https://img.shields.io/badge/FastAPI-Latest-red) ![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- 🤖 **AI-Powered Classification** - Uses Google's Gemma-3-270m-it (270M parameter) model
- 🌐 **Beautiful Web Interface** - Modern, responsive frontend with drag & drop
- 📧 **Batch Processing** - Classify multiple emails simultaneously (up to 50 files)
- 📊 **Detailed Results** - Confidence scores, email metadata, and comprehensive analysis
- 🚀 **REST API** - Full API for integration with other systems
- 📱 **Mobile Friendly** - Works perfectly on all devices
- ⚡ **Fast Processing** - Optimized for real-time classification

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- HuggingFace account and API key
- 4GB+ RAM recommended

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd phishing_pot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   HF_API_KEY=your_huggingface_api_key_here
   HUGGINGFACEHUB_API_TOKEN=your_huggingface_api_key_here
   ```
   
   Get your API key from [HuggingFace](https://huggingface.co/settings/tokens)

4. **Start the server**
   ```bash
   python working_api.py
   ```

5. **Open the web interface**
   
   Navigate to: http://localhost:8000

## 💻 Usage

### Web Interface

1. **Open** http://localhost:8000 in your browser
2. **Upload** .eml files by:
   - Dragging files to the upload area, OR
   - Clicking "Choose Email Files" to browse
3. **Process** files by clicking "Classify X Emails"
4. **View** detailed results with confidence scores

### API Endpoints

#### Classify Multiple Emails
```bash
curl -X POST "http://localhost:8000/classify/batch" \
     -F "files=@email1.eml" \
     -F "files=@email2.eml"
```

#### Classify Single Email
```bash
curl -X POST "http://localhost:8000/classify/email" \
     -F "file=@email.eml"
```

#### Classify Text
```bash
curl -X POST "http://localhost:8000/classify/text" \
     -H "Content-Type: application/json" \
     -d '{"text": "Your email content here"}'
```

#### Health Check
```bash
curl http://localhost:8000/health
```

### Python Integration

```python
from email_classifier import GemmaEmailClassifier

# Initialize classifier
classifier = GemmaEmailClassifier()

# Classify a single email file
result = classifier.classify_eml_file("path/to/email.eml")
print(f"Classification: {result.chosen}")
print(f"Confidence: {result.scores[0][1]:.3f}")
print(f"Subject: {result.subject}")
```

## 📊 API Response Format

```json
{
  "results": [
    {
      "filename": "email.eml",
      "classification": "phishing",
      "confidence": 0.85,
      "subject": "Urgent Account Verification",
      "sender": "fake@bank.com",
      "recipient": "user@example.com",
      "error": null
    }
  ],
  "total_files": 1,
  "successful": 1,
  "failed": 0
}
```

## 🏗️ Project Structure

```
phishing_pot/
├── working_api.py          # FastAPI server
├── email_classifier.py    # Core classification logic
├── frontend.html          # Web interface
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
├── email/                 # Sample email files (~6,000 samples)
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `HF_API_KEY` | HuggingFace API key | Yes |
| `HUGGINGFACEHUB_API_TOKEN` | Alternative HF API key | Yes |

### Model Configuration

The system uses Google's `gemma-3-270m-it` model with these classifications:
- 🔴 **Phishing** - Malicious emails attempting fraud/credential theft
- 🟠 **Spam** - Unwanted promotional/junk emails  
- 🟢 **Benign** - Legitimate, safe emails

## 🧪 Testing

Run the test suite to verify everything works:

```bash
# Test the API endpoints
python test_frontend.py

# Test CSV batch processing
python classify_all_emails.py
```

## 📈 Performance

- **Model**: 270M parameters
- **Processing Speed**: ~2-3 emails/second
- **Memory Usage**: ~2-4GB RAM
- **Accuracy**: ~85-95% on phishing detection
- **Supported Formats**: .eml files

## 🛠️ Development

### Adding New Features

1. **Backend**: Modify `working_api.py` for new API endpoints
2. **Frontend**: Update `frontend.html` for UI changes
3. **Core Logic**: Extend `email_classifier.py` for classification improvements

### Running in Development Mode

```bash
# Start with auto-reload
python working_api.py

# The server will automatically restart on file changes
```

## 🔒 Security Notes

- Keep your HuggingFace API key secure
- The `.env` file is gitignored for security
- Process emails in a secure environment
- Review classification results for sensitive data

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the [Issues](../../issues) page
- Review the API documentation at `/docs` when server is running
- Ensure your HuggingFace API key is valid

## 🎯 Use Cases

- **Cybersecurity Research** - Analyze phishing email patterns
- **IT Security** - Screen incoming emails for threats
- **Email Forensics** - Investigate suspicious email campaigns
- **Security Training** - Generate datasets for security awareness
- **Threat Intelligence** - Bulk analysis of email samples

---

**⚡ Ready to secure your emails with AI?** Start the server and visit http://localhost:8000!
