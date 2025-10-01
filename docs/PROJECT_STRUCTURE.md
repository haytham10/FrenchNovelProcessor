# Project Structure

## Overview
French Novel Processor v2.0 - AI-powered sentence rewriting for French literature.

## Directory Layout

```
FrenchNovelProcessor/
├── docs/                       # Documentation
│   ├── CHANGELOG.md           # Version history and changes
│   ├── DRP.md                 # Development Requirements Plan
│   ├── PROJECT_STRUCTURE.md   # This file
│   ├── MAINTENANCE.md         # Maintenance guide
│   ├── QUICK_REFERENCE.md     # Quick reference
│   └── INDEX.md               # Documentation index
├── scripts/                    # Utility scripts
│   ├── setup.bat              # Initial setup and dependencies
│   ├── run_application.bat    # Quick launcher
│   └── install_gemini.bat     # Gemini API setup
├── src/                        # Source code (organized into packages)
│   ├── __init__.py            # Package initialization
│   ├── core/                  # Core processing modules
│   │   ├── __init__.py
│   │   ├── processor.py       # Main PDF processor
│   │   └── sentence_splitter.py  # Sentence processing logic
│   ├── rewriters/             # AI rewriter modules
│   │   ├── __init__.py
│   │   ├── ai_rewriter.py     # OpenAI integration
│   │   └── gemini_rewriter.py # Gemini AI integration
│   └── utils/                 # Utility modules
│       ├── __init__.py
│       ├── config_manager.py  # Configuration management
│       └── validator.py       # Sentence validation
├── tests/                      # Test files
│   ├── test_basic.py          # Basic functionality tests
│   ├── test_gemini.py         # Gemini API integration tests
│   └── demo.py                # Demo script
├── web_interface/              # Flask web application
│   ├── app.py                 # Flask server
│   ├── static/                # CSS, JS files
│   ├── templates/             # HTML templates
│   ├── uploads/               # Uploaded PDFs (gitignored)
│   └── output/                # Processed files (gitignored)
├── output/                     # CLI output files (gitignored)
├── uploads/                    # CLI upload files (gitignored)
├── .venv/                      # Virtual environment (gitignored)
├── config.ini                  # User configuration (gitignored)
├── config.ini.template        # Configuration template
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git exclusions
└── README.md                  # Main documentation

```

## Core Modules

### Source Code Organization (`src/`)

The source code is organized into logical packages:

#### Core Processing (`src/core/`)
- **processor.py** - NovelProcessor class: Orchestrates PDF processing, OCR, and text extraction
- **sentence_splitter.py** - SentenceSplitter class: Handles sentence splitting and rewriting logic

#### AI Rewriters (`src/rewriters/`)
- **ai_rewriter.py** - AIRewriter class: OpenAI GPT-5 nano integration
- **gemini_rewriter.py** - GeminiRewriter class: Google Gemini 2.5 Flash Lite integration

#### Utilities (`src/utils/`)
- **config_manager.py** - ConfigManager class: Manages configuration and settings
- **validator.py** - SentenceValidator class: Validates sentence structure and word counts

### Configuration
- **config.ini.template** - Template for user configuration
- **config.ini** - User configuration (gitignored, contains API keys)

### Web Interface
- **web_interface/app.py** - Flask web server
- **web_interface/static/** - Frontend assets (CSS, JavaScript)
- **web_interface/templates/** - HTML templates

## Setup Scripts

- **scripts/setup.bat** - One-click setup for Windows
- **scripts/run_application.bat** - Quick launcher for web interface
- **scripts/install_gemini.bat** - Install Gemini API dependencies

## Testing

- **tests/test_basic.py** - Unit tests for core functionality
- **tests/test_gemini.py** - Integration tests for Gemini API
- **tests/demo.py** - Interactive demo script

## Configuration

The application uses `config.ini` for configuration:
- API keys (OpenAI, Gemini)
- Processing modes
- Word limits
- OCR settings

## Data Flow

1. **Input**: User uploads PDF via web interface or CLI
2. **Processing**: 
   - Extract text using OCR (if needed)
   - Detect language
   - Split/rewrite sentences based on mode
   - Validate output
3. **Output**: Generate CSV/TXT files with processed text

## API Options

The application supports two AI providers:
- **OpenAI** (GPT-5 nano) - Fastest & cheapest, recommended for production
- **Gemini** (2.5 Flash Lite) - Free tier available

Users can switch between providers in the settings.
