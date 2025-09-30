# Changelog - French Novel Processor

All notable changes to this project will be documented in this file.

## [2.0.0] - 2025-10-03

### Added - AI Amendment
- **AI-Powered Sentence Rewriting**: Integrated OpenAI GPT-4o-mini for intelligent sentence rewriting
- **Configuration Manager**: New `config_manager.py` for managing settings and API keys
- **AI Rewriter Module**: New `ai_rewriter.py` with OpenAI integration, retry logic, and cost tracking
- **Validation System**: New `validator.py` for quality checking rewritten sentences
  - Word count validation
  - French language detection
  - Content preservation scoring
- **Enhanced Sentence Splitter**: Updated `sentence_splitter.py` to support both AI and mechanical modes
- **Cost Estimation**: Real-time cost tracking and estimation during processing
- **Processing Statistics**: Detailed stats showing direct, AI-rewritten, and mechanical-chunked sentences
- **Web Interface Enhancements**:
  - Settings panel for API key configuration
  - Processing mode selection (AI vs. Mechanical)
  - Real-time progress tracking with detailed statistics
  - Cost display during and after processing
  - Enhanced error handling and user feedback
- **Configuration Template**: `config.ini.template` for easy setup
- **API Key Management**: Secure local storage of API keys
- **API Key Testing**: Validate API keys before processing
- **Processing Logs**: Optional detailed logs of all rewrites and processing decisions
- **Enhanced Output Format**: 
  - Added "Original" column to show source sentences
  - Added "Method" column to track processing method
  - Added "Word_Count" column
  - Separate processing log sheet with detailed information

### Changed
- **Processor Module**: Enhanced `processor.py` to support new processing modes
- **Output Generation**: Improved DataFrame generation with mode-specific columns
- **Progress Tracking**: More detailed progress callbacks with sentence-level information
- **Setup Script**: Updated `setup.bat` to install new dependencies (openai, langdetect, tenacity)
- **Requirements**: Added AI-related dependencies to `requirements.txt`

### Enhanced
- **Error Handling**: Comprehensive error handling with automatic fallback to mechanical chunking
- **Retry Logic**: Automatic retry with exponential backoff for API failures
- **Validation**: Multi-level validation ensuring quality output
- **User Experience**: 
  - First-run setup wizard for API key
  - Clear status messages and error feedback
  - Estimated cost before and during processing
  - Processing time estimates

### Maintained
- **Backward Compatibility**: Legacy mechanical chunking mode still available
- **All Original Features**: PDF processing, OCR, text extraction, CSV/Excel export
- **Existing UI**: Enhanced but maintains familiar layout

### Technical Improvements
- Token counting and cost calculation
- Language detection for output validation
- Content preservation checking
- Graceful degradation on API failures
- Asynchronous processing with progress updates
- Proper resource management and cleanup

### Documentation
- Comprehensive README with setup instructions
- API key acquisition guide
- Cost information and estimates
- Troubleshooting section
- Detailed changelog
- Configuration file documentation

### Dependencies Added
```
openai==1.12.0       # OpenAI API client
langdetect==1.0.9    # Language detection
tenacity==8.2.3      # Retry logic
```

### Security
- API keys stored locally in config file (not in code)
- No credentials transmitted except to OpenAI API
- Secure file handling for uploads and outputs

### Performance
- Processing time: 15-20 minutes for 350-page novel (AI mode)
- Processing time: 5-10 minutes for 350-page novel (legacy mode)
- Memory efficient processing with streaming
- Cost: $2-5 per typical novel

---

## [1.0.0] - 2025-09-29

### Initial Release
- PDF text extraction with PyPDF2
- OCR support with Tesseract for scanned PDFs
- Mechanical sentence chunking (8 words per chunk)
- Google Sheets export
- CSV export
- Web-based user interface with Flask
- Drag-and-drop file upload
- Progress tracking
- Batch processing support
- Windows batch file launchers

### Features
- PDF processing from local files
- Configurable word limit per sentence
- Simple mechanical splitting algorithm
- Clean web interface
- Real-time progress updates
- Multiple output formats (Google Sheets, CSV)

### Dependencies
- Flask for web interface
- PyPDF2 for PDF text extraction
- pytesseract for OCR
- pdf2image for image conversion
- pandas for data processing
- Google API client for Sheets integration

---

## Version Comparison

| Feature | v1.0 | v2.0 |
|---------|------|------|
| PDF Processing | ✅ | ✅ |
| OCR Support | ✅ | ✅ |
| Mechanical Chunking | ✅ | ✅ |
| AI Rewriting | ❌ | ✅ |
| Cost Tracking | ❌ | ✅ |
| Quality Validation | ❌ | ✅ |
| Processing Logs | ❌ | ✅ |
| API Key Management | ❌ | ✅ |
| Mode Selection | ❌ | ✅ |
| Enhanced Output | ❌ | ✅ |

---

## Upgrade Notes

### From v1.0 to v2.0

1. **No Breaking Changes**: All v1.0 functionality preserved
2. **New Dependencies**: Run `setup.bat` to install new packages
3. **Optional API Key**: Only needed if using AI mode
4. **Legacy Mode Available**: Can still use mechanical chunking
5. **Enhanced Output**: New columns added but existing columns unchanged
6. **Configuration**: New `config.ini` file created on first run

### Migration Steps

1. Back up your v1.0 installation (optional)
2. Extract v2.0 files
3. Run `setup.bat` to install new dependencies
4. (Optional) Get OpenAI API key if using AI mode
5. Run `run_application.bat` as before
6. Configure API key in settings if using AI mode

### New Costs

- **AI Mode**: $2-5 per novel (OpenAI API charges)
- **Legacy Mode**: Free (no changes from v1.0)

---

## Roadmap

### Future Considerations (Not Committed)
- Local AI model option (Llama, Mistral)
- Support for Claude, Anthropic models
- Batch processing interface
- Manual sentence editing
- Quality scoring system
- Rewrite caching
- Multi-language support beyond French
- PDF annotations for changes
- Cloud deployment option

---

**Developer**: Haytham Mokhtari  
**Client**: Stan Jones  
**Project**: French Novel Processor Amendment  
**Timeline**: September 30 - October 3, 2025
