# Quick Reference Guide

## Command Line Quick Start

```bash
# Setup (first time only)
scripts\setup.bat

# Run web interface
scripts\run_application.bat

# Install Gemini support
scripts\install_gemini.bat

# Run tests
python tests\test_basic.py
python tests\test_gemini.py

# Run demo
python tests\demo.py
```

## Configuration Files

### config.ini Structure
```ini
[OpenAI]
api_key = sk-...

[Gemini]
gemini_api_key = ...

[Processing]
word_limit = 8
use_gemini_dev = false
```

## API Endpoints (Web Interface)

### Settings
- `GET /api/settings` - Get current settings
- `POST /api/settings` - Update settings
- `POST /api/test-api-key` - Test OpenAI key
- `POST /api/test-gemini-key` - Test Gemini key

### Processing
- `POST /api/upload` - Upload PDF
- `POST /api/process` - Process uploaded file
- `GET /api/progress` - Check processing status
- `GET /api/download/<filename>` - Download results

## Processing Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `mechanical` | 8-word chunks | Fast, no API needed |
| `ai_rewrite` | OpenAI GPT-5 nano | High quality, fastest & cheapest |
| `gemini_rewrite` | Gemini 2.5 Flash Lite | Free tier available |

## Cost Estimates

### OpenAI (GPT-5 nano)
- Input: $0.05 per 1M tokens
- Output: $0.40 per 1M tokens
- Typical novel (350 pages): $0.50-1

### Gemini (2.5 Flash Lite)
- Input: $0.10 per 1M tokens
- Output: $0.40 per 1M tokens
- Free tier: 15 RPM, 1500 RPD
- Lower cost alternative

## Common Tasks

### Change AI Provider
1. Open Settings
2. Select provider (OpenAI/Gemini)
3. Enter API key
4. Click Test
5. Click Save

### Process a PDF
1. Upload PDF file
2. Set word limit (default: 8)
3. Choose processing mode
4. Click Start Processing
5. Wait for completion
6. Download results

### Check Processing Status
- Progress bar shows completion %
- Status messages show current step
- Estimated time remaining displayed
- Token usage tracked in real-time

## File Formats

### Input
- PDF files (text or scanned)
- Supported languages: French (primary)

### Output
- CSV format with columns:
  - Original Sentence
  - Rewritten Sentences
  - Word Count
  - Method Used
  - Timestamp

## Troubleshooting Quick Fixes

### Problem: "API Key Invalid"
```bash
# Check config.ini has correct key
# Key should start with "sk-" (OpenAI) or be valid Gemini key
# Test using Settings → Test button
```

### Problem: "Module Not Found"
```bash
# Activate virtual environment
.venv\Scripts\activate
# Reinstall dependencies
pip install -r requirements.txt
```

### Problem: "OCR Failed"
```bash
# Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
# Install Poppler: https://github.com/oschwartz10612/poppler-windows/releases
# Add both to system PATH
```

### Problem: "Port Already in Use"
```bash
# Find process using port 5000
netstat -ano | findstr :5000
# Kill the process
taskkill /PID <process_id> /F
```

## Keyboard Shortcuts (Web Interface)

- `Ctrl+U` - Focus upload area
- `Ctrl+S` - Open settings (when not in input)
- `Esc` - Close modal
- `Enter` - Submit form (when focused)

## File Locations

```
config.ini              → User settings
output/                 → CLI processed files
web_interface/output/   → Web processed files
web_interface/uploads/  → Uploaded PDFs
requirements.txt        → Python dependencies
.venv/                  → Virtual environment
```

## Python Module Reference

### Import Paths
```python
from src.core.processor import NovelProcessor
from src.core.sentence_splitter import SentenceSplitter, ProcessingMode
from src.rewriters.ai_rewriter import AIRewriter
from src.rewriters.gemini_rewriter import GeminiRewriter
from src.utils.validator import SentenceValidator
from src.utils.config_manager import ConfigManager
```

### Quick Example
```python
from src.utils.config_manager import ConfigManager
from src.core.sentence_splitter import SentenceSplitter, ProcessingMode

config = ConfigManager()
splitter = SentenceSplitter(
    word_limit=8,
    mode=ProcessingMode.AI_REWRITE,
    api_key=config.get_openai_api_key()
)

sentences = ["Long French sentence..."]
results = splitter.process_sentences(sentences)
```

## Environment Variables

```bash
# Optional: Override config.ini
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="..."

# Set log level
export LOG_LEVEL="DEBUG"

# Set Flask environment
export FLASK_ENV="development"
```

## Docker Support (Future)

```dockerfile
# Coming soon - containerized deployment
docker build -t french-processor .
docker run -p 5000:5000 french-processor
```

## Browser Compatibility

### Supported Browsers
- Chrome 90+ ✅
- Firefox 88+ ✅
- Edge 90+ ✅
- Safari 14+ ✅

### Required Features
- JavaScript enabled
- Cookies enabled
- Local storage access
- Drag and drop API

## Performance Tips

1. **Batch Processing**: Process multiple files in sequence
2. **Cache Responses**: Identical sentences reuse results
3. **Optimize Prompts**: Shorter prompts = lower costs
4. **Use Gemini Free Tier**: 1500 requests/day free
5. **Monitor Token Usage**: Track costs in real-time

## Support Resources

- Documentation: `docs/`
- Tests: `tests/`
- Examples: `tests/demo.py`
- Structure: `docs/PROJECT_STRUCTURE.md`
- Maintenance: `docs/MAINTENANCE.md`
- Changelog: `docs/CHANGELOG.md`

## Version Information

Current Version: 2.0
Python Required: 3.8+
Platform: Windows
License: Proprietary

---

For detailed information, see the full README.md and documentation in `docs/`.
