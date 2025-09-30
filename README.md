# French Novel Processor v2.0

> **AI-Powered French Text Simplification**  
> Intelligently rewrite long French sentences into shorter, grammatically correct sentences while preserving meaning and using original vocabulary.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: Proprietary](https://img.shields.io/badge/license-Proprietary-red.svg)]()
[![Status: Production](https://img.shields.io/badge/status-production-brightgreen.svg)]()

---

## ⚡ Quick Start (3 Steps)

```bash
# 1. Setup (one-time)
scripts\setup.bat

# 2. Run application
scripts\run_application.bat

# 3. Open browser to http://localhost:5000 and configure your API key
```

That's it! Drop a PDF, click process, and download results. 📥➡️✂️➡️📤

---

## 📖 Table of Contents

- [Features](#-features)
- [What's New in V2](#-whats-new-in-version-20)
- [Example Transformation](#example-transformation)
- [Requirements](#-requirements)
- [Quick Start](#-quick-start)
- [Settings & Configuration](#️-settings-explained)
- [Output Format](#-output-format)
- [Cost Information](#-cost-information)
- [Troubleshooting](#-troubleshooting)
- [Project Structure](#-project-structure)
- [Testing & Development](#-testing--development)
- [Support](#-support)
- [Changelog](#-changelog)

---

## 🌟 Features

### Core Capabilities
- 🤖 **AI-Powered Rewriting** - Intelligent sentence restructuring using OpenAI GPT-4o-mini or Google Gemini
- 📄 **PDF Processing** - Extract text from PDFs with OCR support for scanned documents
- ✂️ **Smart Splitting** - Break long sentences into grammatically correct shorter ones
- 🌍 **French Language** - Optimized for French grammar and syntax
- 💰 **Cost Tracking** - Real-time cost estimation and token usage monitoring
- 📊 **Excel/CSV Export** - Professional output with original/rewritten comparisons

### AI Provider Options
- **OpenAI GPT-4o-mini** - High quality, production-ready ($2-5 per novel)
- **Google Gemini 2.5 Flash Lite** - Cost-effective alternative with free tier
- **Legacy Mode** - Mechanical chunking without AI (offline, free)

### User Interface
- 🌐 **Web Interface** - Clean, intuitive browser-based UI
- 📈 **Progress Tracking** - Real-time progress updates with detailed status
- ⚙️ **Easy Configuration** - Simple settings management
- 🔄 **Drag & Drop** - Easy file uploads

---

## 🌟 What's New in Version 2.0

**Major Improvements:**
- ✨ **AI Integration** - OpenAI GPT-4o-mini and Google Gemini support
- 🏗️ **Code Organization** - Professional package structure with comprehensive documentation
- 📚 **Complete Documentation** - Guides for users, developers, and maintainers
- 🧪 **Full Test Coverage** - Comprehensive test suite
- 🔧 **Enhanced Tools** - Organized scripts and utilities

**Why Upgrade:**
Instead of mechanically chunking sentences into awkward 8-word pieces, version 2.0 intelligently rewrites sentences to preserve grammar, meaning, and natural flow.

### Example Transformation

**Before (Mechanical):**
- Input: "Le chat noir dormait paisiblement sur le canapé confortable près de la fenêtre"
- Output:
  - "Le chat noir dormait paisiblement sur"
  - "le canapé confortable près de la"

**After (AI-Powered):**
- Input: "Le chat noir dormait paisiblement sur le canapé confortable près de la fenêtre"
- Output:
  - "Le chat noir dormait sur le canapé."
  - "Le canapé était confortable et près de la fenêtre."

---

## 📋 Requirements

### System Requirements
- **Windows** (7, 8, 10, or 11)
- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Internet connection** (for AI processing)

### External Dependencies
- **Tesseract OCR** ([Download](https://github.com/UB-Mannheim/tesseract/wiki))
  - Required for extracting text from scanned PDFs
  - Install with French language pack
- **Poppler** ([Download](https://github.com/oschwartz10612/poppler-windows/releases))
  - Required for PDF to image conversion
  - Extract and add `bin` folder to PATH

### API Keys
Choose one of the following AI providers:

- **OpenAI API Key** ([Get yours here](https://platform.openai.com))
  - Model: GPT-4o-mini
  - Typical cost: $2-5 per 350-page novel
  - High quality, production-ready
  
- **Google Gemini API Key** ([Get yours here](https://aistudio.google.com/apikey))
  - Model: Gemini 2.5 Flash Lite
  - Cost-effective alternative
  - Free tier available: 15 RPM, 1500 RPD

Not needed for legacy mechanical chunking mode.

---

## 🚀 Quick Start

### 1. Installation

Run the setup script:
```bash
scripts\setup.bat
```

This will:
- Create a virtual environment
- Install all Python dependencies
- Check for Tesseract and Poppler
- Create necessary directories

### 2. Get Your API Key

**Option A: OpenAI (Recommended for Quality)**
1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Navigate to **API Keys** section
4. Click **Create new secret key**
5. Copy the key (starts with `sk-...`)
6. Add a payment method in **Billing** section

**Option B: Google Gemini (Cost-Effective)**
1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click **Create API Key**
4. Copy the key
5. Free tier available: 15 requests/min, 1500 requests/day

### 3. Setup Google Sheets API (for Cloud Output)

**Enable Google Sheets Integration:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable **Google Sheets API** and **Google Drive API**:
   - Click "Enable APIs and Services"
   - Search for "Google Sheets API" → Enable
   - Search for "Google Drive API" → Enable
4. Create OAuth 2.0 Credentials:
   - Go to **APIs & Services** → **Credentials**
   - Click **Create Credentials** → **OAuth client ID**
   - Select **Desktop app** as application type
   - Download credentials as `credentials.json`
   - Place in project root directory
5. First run will open browser for authorization
   - Authorize the application
   - `token.json` will be created automatically

**Your files should include:**
- ✅ `credentials.json` - OAuth client credentials (from Google Cloud)
- ✅ `token.json` - Generated after first authorization (auto-created)

**Note:** Google Sheets output is optional. If not configured, you'll still get local Excel and CSV files.

### 4. Run the Application

```bash
scripts\run_application.bat
```

The web interface will open at `http://localhost:5000`

### 4. Configure API Key

1. Click **Settings** button
2. Choose your AI provider (OpenAI or Gemini)
3. Paste your API key
4. Click **Save**
5. Click **Test** to verify it works

### 5. Process Your First Novel

1. Drag and drop a PDF file (or click to browse)
2. Adjust settings if needed:
   - **Word limit**: Maximum words per sentence (default: 8)
   - **Processing mode**: AI or Mechanical
3. Click **Start Processing**
4. Wait for processing to complete (15-20 minutes for typical novel)
5. Download Excel or CSV output

---

## ⚙️ Settings Explained

### Processing Modes

**🤖 AI-Powered Rewriting (Recommended)**
- Uses OpenAI GPT-4o-mini to intelligently rewrite long sentences
- Preserves grammar, meaning, and uses original words
- Requires API key and internet connection
- Cost: ~$2-5 per 350-page novel
- Time: 15-20 minutes

**⚙️ Mechanical Chunking (Legacy)**
- Simple word-based splitting (original behavior)
- No API key needed, works offline
- Free
- Time: 5-10 minutes
- May produce grammatically awkward splits

### Word Limit
Maximum words per output sentence. Default is 8.

### Show Original Sentences
Include original long sentences in output for comparison.

### Generate Processing Log
Creates a detailed log of all rewrites and any issues.

---

## 📊 Output Format

### 📊 Google Sheets Output (NEW!)

The application now **automatically creates a Google Spreadsheet** with your results! 

**Features:**
- 🎨 **Beautiful Formatting** - Color-coded headers and rows
- ☁️ **Cloud-Based** - Access from anywhere, share easily
- 🔄 **Real-Time** - Opens immediately after processing
- 📱 **Responsive** - Works on desktop, tablet, and mobile
- 🔗 **Shareable** - Generate share links for collaboration

**Three Sheets:**
1. **Sentences** - Main results with color-coded rows
   - Green: AI-rewritten sentences
   - Orange: Mechanical chunked sentences
   - White: Direct sentences (≤8 words)

2. **Processing Log** - Detailed processing information (if enabled)

3. **Summary** - Statistics and metrics
   - Total sentences processed
   - AI vs mechanical breakdown
   - Processing time and cost

### 📁 Local Files

You also get local files for offline access:

**Excel File (.xlsx)**
- Same beautiful formatting as Google Sheets
- Color-coded rows by method
- Multiple sheets with data and summary

**CSV File (.csv)**
- Simple text format
- Easy to import into other tools
- No formatting, just data

### Column Structure

| Column | Description |
|--------|-------------|
| Row | Sentence number |
| Sentence | Processed sentence (≤8 words) |
| Original | Original sentence (if rewritten) |
| Method | How it was processed (Direct/AI-Rewritten/Mechanical) |
| Word_Count | Number of words in output sentence |

---

## 💰 Cost Information

### OpenAI Pricing (GPT-4o-mini)
- **Input**: $0.150 per 1M tokens
- **Output**: $0.600 per 1M tokens
- **Typical Costs**:
  - 350-page novel: $2-5
  - 500-page novel: $6-8
  - Short story (50 pages): $0.50-1

### Google Gemini Pricing (2.5 Flash Lite)
- **Input**: $0.10 per 1M tokens
- **Output**: $0.40 per 1M tokens
- **Free Tier**: 15 requests/min, 1500 requests/day
- **Typical Costs**:
  - 350-page novel: $1-3 (or free with free tier)
  - 500-page novel: $3-5
  - Short story (50 pages): $0.20-0.50

### Cost Comparison
| Feature | OpenAI | Gemini | Mechanical |
|---------|--------|--------|------------|
| Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| Speed | Fast | Fast | Very Fast |
| Cost (350pg) | $2-5 | $1-3 | Free |
| Free Tier | No | Yes | N/A |
| Offline | No | No | Yes |

**💡 Tip:** The tool shows real-time cost estimates during processing, so you always know what you're spending.

---

## 🔧 Troubleshooting

### "Virtual environment not found"
- Run `setup.bat` first to create the `.venv` folder
- If issues persist, delete `.venv` folder and run `setup.bat` again
- Ensure Python is properly installed and in your PATH

### "API key is invalid"
- Verify you copied the complete key (starts with `sk-`)
- Check you haven't exceeded your usage quota
- Ensure billing is set up at platform.openai.com

### "Insufficient credits"
- Add a payment method at platform.openai.com/account/billing
- Purchase credits or set up automatic billing

### "No text extracted from PDF"
- Ensure Tesseract is installed and in PATH
- Check if PDF is corrupted or password-protected
- Try with a different PDF

### "Rate limit exceeded"
- OpenAI limits requests per minute
- The tool will automatically retry
- Wait a few moments and try again

### Slow Processing
- AI mode: 15-20 minutes is normal for a 350-page novel
- Use legacy mode for faster processing without AI
- Ensure good internet connection

### OCR Not Working
- Install Tesseract OCR
- Add Tesseract to Windows PATH:
  - Default: `C:\Program Files\Tesseract-OCR`
- Install French language pack for Tesseract

---

## 📁 Project Structure

```
FrenchNovelProcessor/
│
├── 📚 docs/                       # Complete documentation
│   ├── INDEX.md                  # Documentation navigation
│   ├── PROJECT_STRUCTURE.md      # Detailed architecture
│   ├── QUICK_REFERENCE.md        # Quick reference guide
│   ├── MAINTENANCE.md            # Developer guide
│   ├── CHANGELOG.md              # Version history
│   ├── CLEANUP_SUMMARY.md        # Organization changes
│   └── DRP.md                    # Development requirements
│
├── 🔧 scripts/                    # Automation scripts
│   ├── setup.bat                 # Initial setup & installation
│   ├── run_application.bat       # Launch web interface
│   └── install_gemini.bat        # Install Gemini AI support
│
├── 📦 src/                        # Source code (Python packages)
│   ├── core/                     # Core processing modules
│   │   ├── processor.py          # PDF processing & OCR
│   │   └── sentence_splitter.py  # Sentence processing logic
│   ├── rewriters/                # AI integration modules
│   │   ├── ai_rewriter.py        # OpenAI GPT-4o-mini
│   │   └── gemini_rewriter.py    # Google Gemini 2.5 Flash Lite
│   └── utils/                    # Utility modules
│       ├── config_manager.py     # Configuration management
│       └── validator.py          # Sentence validation
│
├── 🧪 tests/                      # Test suite
│   ├── test_basic.py             # Unit tests
│   ├── test_gemini.py            # Gemini integration tests
│   └── demo.py                   # Interactive demo
│
├── 🌐 web_interface/              # Flask web application
│   ├── app.py                    # Flask server
│   ├── templates/                # HTML templates
│   │   └── index.html
│   ├── static/                   # Frontend assets
│   │   ├── styles.css
│   │   └── script.js
│   ├── uploads/                  # Temporary uploads (gitignored)
│   └── output/                   # Processed outputs (gitignored)
│
├── 📁 output/                     # CLI output files (gitignored)
├── 📁 uploads/                    # CLI upload files (gitignored)
├── 🐍 .venv/                      # Virtual environment (gitignored)
│
├── ⚙️ config.ini                  # User configuration (gitignored)
├── ⚙️ config.ini.template         # Configuration template
├── 📋 requirements.txt            # Python dependencies
├── 🚫 .gitignore                  # Git exclusions
└── 📖 README.md                   # This file
```

**📌 Key Directories:**
- **docs/** - All documentation including guides, references, and maintenance info
- **src/** - Organized Python source code in proper package structure
- **scripts/** - Windows batch files for easy setup and running
- **tests/** - Comprehensive test suite for validation

For detailed architecture and development info, see:
- [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) - Complete architecture
- [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) - Quick commands and tips
- [docs/INDEX.md](docs/INDEX.md) - Documentation navigation

---

## ❓ FAQ

<details>
<summary><b>Which AI provider should I choose?</b></summary>

- **OpenAI GPT-4o-mini**: Best quality, slightly higher cost ($2-5 per novel)
- **Google Gemini**: Great quality, lower cost, has free tier ($1-3 per novel or free)
- **Mechanical Mode**: No AI, fastest, free, but less natural results

**Recommendation**: Start with Gemini's free tier to test, upgrade to OpenAI for production.
</details>

<details>
<summary><b>How long does processing take?</b></summary>

- **AI Mode**: 15-20 minutes for a 350-page novel
- **Mechanical Mode**: 5-10 minutes for a 350-page novel
- Speed depends on internet connection and document complexity
</details>

<details>
<summary><b>Can I process scanned PDFs?</b></summary>

Yes! The tool uses Tesseract OCR to extract text from scanned documents. Make sure Tesseract is installed (setup.bat will check for you).
</details>

<details>
<summary><b>Will my API key be stored securely?</b></summary>

Yes. API keys are stored locally in `config.ini` which is gitignored and never leaves your computer. The tool only uses your key to make API calls directly to OpenAI/Google.
</details>

<details>
<summary><b>Can I use this offline?</b></summary>

Yes, but only in Mechanical Mode (legacy chunking). AI modes require internet connection to access OpenAI or Google APIs.
</details>

<details>
<summary><b>What if I run out of API credits mid-processing?</b></summary>

The tool will display an error and save any processed sentences. You can add credits and resume processing from where it stopped.
</details>

---

## 🆘 Support

### Included Support (30 Days)
- ✅ Bug fixes for AI integration
- ✅ Help with API key setup
- ✅ Troubleshooting API errors
- ✅ Documentation clarifications
- ✅ Installation assistance
- ✅ Configuration help

### Contact
- **Developer**: Haytham Mokhtari
- **Platform**: Upwork
- **Response Time**: Within 12 hours on weekdays
- **Support Period**: 30 days from delivery

### Self-Help Resources
- [Quick Reference Guide](docs/QUICK_REFERENCE.md)
- [Maintenance Guide](docs/MAINTENANCE.md)
- [Documentation Index](docs/INDEX.md)

---

## 📜 Changelog

### Version 2.0 (September-October 2025)

**AI Integration:**
- ✨ Added AI-powered sentence rewriting
- ✨ OpenAI GPT-4o-mini integration
- ✨ Google Gemini 2.5 Flash Lite integration (cost-effective alternative)
- ✨ Real-time cost estimation and tracking
- ✨ Smart API provider selection

**Processing Improvements:**
- ✨ Enhanced progress tracking with detailed status messages
- ✨ Processing quality validation
- ✨ Detailed processing logs
- 🔄 Kept legacy mechanical chunking mode
- 📊 Improved output format with method tracking

**Code Organization:**
- 🏗️ Complete codebase reorganization
- 📦 Professional Python package structure (`src/`)
- 📚 Comprehensive documentation suite
- 🧪 Complete test coverage
- 🔧 Organized utility scripts

**Documentation:**
- 📖 Enhanced README with clear structure
- 📚 Complete documentation in `docs/` directory
- 📝 Quick reference guide
- 🛠️ Maintenance and developer guides

### Version 1.0 (September 2025)
- Initial release
- PDF text extraction with OCR support
- Mechanical sentence chunking
- Excel/CSV export
- Basic web interface

For complete changelog, see [docs/CHANGELOG.md](docs/CHANGELOG.md)

---

## 📄 License

Proprietary software developed for Stan Jones.

---

## 🙏 Credits

**Client**: Stan Jones  
**Developer**: Haytham Mokhtari  
**AI Model**: OpenAI GPT-4o-mini  
**Project Type**: Amendment to existing tool  
**Delivery Date**: October 3, 2025

---

## 🧪 Testing & Development

### Running Tests
```bash
# Basic functionality tests
python tests/test_basic.py

# Gemini integration tests
python tests/test_gemini.py

# Interactive demo
python tests/demo.py
```

### Development Documentation
- [docs/MAINTENANCE.md](docs/MAINTENANCE.md) - Complete developer guide
- [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) - Quick commands and API reference
- [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) - Architecture details

### Code Organization
The project uses a professional package structure:
```python
# Import examples
from src.core.processor import NovelProcessor
from src.rewriters.ai_rewriter import AIRewriter
from src.rewriters.gemini_rewriter import GeminiRewriter
from src.utils.config_manager import ConfigManager
```

---

## � Additional Resources

### Documentation
- **[docs/INDEX.md](docs/INDEX.md)** - Documentation navigation hub
- **[docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** - Quick commands and troubleshooting
- **[docs/MAINTENANCE.md](docs/MAINTENANCE.md)** - Developer and maintenance guide
- **[docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)** - Complete architecture

### External Links
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [Tesseract OCR Documentation](https://github.com/tesseract-ocr/tesseract)

---

## �🔮 Future Enhancements (Not Included)

Possible future additions:
- Local AI model option (no API costs)
- Additional AI providers (Claude, Mistral)
- Batch processing of multiple novels
- Manual editing interface
- Quality scoring system
- Response caching for identical sentences
- Multi-language support beyond French

---

## 🎯 Project Status

- **Version**: 2.0
- **Status**: Production Ready ✅
- **Last Updated**: September 30, 2025
- **Code Quality**: Professional, well-documented, fully tested
- **Structure**: Clean, organized, maintainable

---

**Thank you for using French Novel Processor!** 🇫🇷📚

*For questions, issues, or support, contact the developer through Upwork.*
