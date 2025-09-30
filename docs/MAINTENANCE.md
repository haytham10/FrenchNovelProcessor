# Maintenance Guide

## Code Organization

### Directory Structure
The codebase follows a clean separation of concerns:

- **Root**: Core Python modules (processors, rewriters, validators)
- **docs/**: All documentation files
- **scripts/**: Batch files for Windows automation
- **tests/**: Test files and demo scripts
- **web_interface/**: Flask web application

### Code Style
- Follow PEP 8 guidelines
- Use type hints where applicable
- Document functions with docstrings
- Keep functions focused and single-purpose

## Adding New Features

### Adding a New AI Provider

1. Create a new rewriter file: `{provider}_rewriter.py`
2. Implement the same interface as `ai_rewriter.py`:
   - `__init__(api_key, word_limit, model)`
   - `validate_api_key()` → Tuple[bool, str]
   - `rewrite_sentence(sentence)` → List[str]
   - `get_token_stats()` → dict
   - `get_current_cost()` → float

3. Update `config_manager.py`:
   - Add getter/setter for API key
   - Add configuration flag
   - Update `should_use_*` logic

4. Update `sentence_splitter.py`:
   - Add conditional import
   - Update rewriter selection logic

5. Update web interface:
   - Add UI in `templates/index.html`
   - Add endpoints in `app.py`
   - Add client logic in `static/script.js`

### Adding New Processing Modes

1. Update `ProcessingMode` enum in `sentence_splitter.py`
2. Implement processing logic in `SentenceSplitter.process_sentences()`
3. Add mode selection in web interface
4. Update documentation

## Testing

### Running Tests

```bash
# Activate virtual environment
source .venv/Scripts/activate  # Unix/Mac
.venv\Scripts\activate        # Windows

# Run specific tests
python tests/test_basic.py
python tests/test_gemini.py

# Run demo
python tests/demo.py
```

### Writing Tests

Place test files in `tests/` directory:
- `test_*.py` for unit tests
- Use descriptive function names
- Mock external API calls
- Test edge cases

## Deployment

### Local Deployment

1. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure `config.ini` with API keys

3. Run the application:
   ```bash
   scripts\run_application.bat
   ```

### Production Considerations

- Use a production WSGI server (Gunicorn, uWSGI)
- Set `DEBUG=False` in Flask
- Use environment variables for API keys
- Implement rate limiting
- Add error logging
- Set up monitoring

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Solution: Activate virtual environment
   - Check: `pip list` shows all dependencies

2. **API Key Errors**
   - Solution: Verify key in `config.ini`
   - Test: Use validation endpoints

3. **OCR Not Working**
   - Solution: Install Tesseract and Poppler
   - Check: Add to system PATH

4. **Cache Issues**
   - Solution: Clear Python cache
   ```bash
   find . -type d -name "__pycache__" -delete
   find . -type f -name "*.pyc" -delete
   ```

## Code Quality

### Pre-commit Checklist
- [ ] Remove debug print statements
- [ ] Update docstrings
- [ ] Run tests
- [ ] Check for unused imports
- [ ] Verify error handling
- [ ] Update CHANGELOG.md

### Performance Tips
- Cache AI responses for identical sentences
- Use batch processing for multiple files
- Implement async processing for web uploads
- Optimize token usage in prompts

## Security

### API Key Security
- Never commit `config.ini` to version control
- Use environment variables in production
- Rotate keys regularly
- Implement rate limiting

### File Upload Security
- Validate file types
- Limit file sizes
- Scan for malicious content
- Clean up temporary files

## Updating Dependencies

```bash
# Check outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package_name

# Update all packages (careful!)
pip install --upgrade -r requirements.txt

# Freeze new requirements
pip freeze > requirements.txt
```

## Backup and Recovery

### Important Files to Backup
- `config.ini` (API keys, settings)
- `output/` directory (processed files)
- `uploads/` directory (source PDFs)

### Recovery Steps
1. Reinstall dependencies: `scripts\setup.bat`
2. Restore `config.ini`
3. Test API connections
4. Verify processing works

## Contributing

### Code Review Checklist
- Code follows project structure
- Tests are included
- Documentation is updated
- No breaking changes to API
- Backwards compatible

### Git Workflow
1. Create feature branch
2. Make changes
3. Test thoroughly
4. Update documentation
5. Submit pull request

## Monitoring

### Key Metrics
- API response times
- Token usage per document
- Processing success rate
- Error rates by type
- Cost per document

### Logging
- All logs in `output/*.log`
- Include timestamps
- Log levels: DEBUG, INFO, WARNING, ERROR
- Track API calls and costs

## Future Improvements

### Planned Features
- Local AI model support
- Multi-language support
- Advanced caching system
- Batch processing queue
- User authentication

### Technical Debt
- Refactor large functions
- Add comprehensive unit tests
- Improve error messages
- Optimize token usage
- Add type hints everywhere
