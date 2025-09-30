"""
Flask Web Interface for French Novel Processor
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import threading
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.config_manager import ConfigManager
from src.core.processor import NovelProcessor
from src.rewriters.ai_rewriter import AIRewriter

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Global state
config_manager = ConfigManager()
processing_status = {
    'is_processing': False,
    'progress': 0,
    'status_message': '',
    'current_sentence': '',
    'stats': {},
    'error': None,
    'output_file': None
}


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current settings"""
    return jsonify({
        'api_key': config_manager.get_api_key() or '',
        'api_key_configured': bool(config_manager.get_api_key()),
        'gemini_api_key': config_manager.get_gemini_api_key() or '',
        'gemini_api_key_configured': bool(config_manager.get_gemini_api_key()),
        'use_gemini_dev': config_manager.get_use_gemini_dev(),
        'word_limit': config_manager.get_word_limit(),
        'processing_mode': config_manager.get_processing_mode(),
        'show_original': config_manager.get_show_original(),
        'generate_log': config_manager.get_generate_log()
    })


@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update settings"""
    try:
        data = request.json
        
        if 'api_key' in data:
            config_manager.set_api_key(data['api_key'])
        
        if 'gemini_api_key' in data:
            config_manager.set_gemini_api_key(data['gemini_api_key'])
        
        if 'use_gemini_dev' in data:
            config_manager.set_use_gemini_dev(data['use_gemini_dev'])
        
        if 'word_limit' in data:
            config_manager.set_word_limit(int(data['word_limit']))
        
        if 'processing_mode' in data:
            config_manager.set_processing_mode(data['processing_mode'])
        
        if 'show_original' in data:
            config_manager.set_show_original(data['show_original'])
        
        if 'generate_log' in data:
            config_manager.set_generate_log(data['generate_log'])
        
        return jsonify({'success': True, 'message': 'Settings saved successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/test-api-key', methods=['POST'])
def test_api_key():
    """Test OpenAI API key"""
    try:
        data = request.json
        api_key = data.get('api_key')
        
        if not api_key:
            return jsonify({'success': False, 'error': 'API key required'}), 400
        
        # Test the key
        rewriter = AIRewriter(api_key)
        is_valid, message = rewriter.validate_api_key()
        
        return jsonify({'success': is_valid, 'message': message})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/test-gemini-key', methods=['POST'])
def test_gemini_key():
    """Test Gemini API key"""
    try:
        data = request.json
        api_key = data.get('api_key')
        
        if not api_key:
            return jsonify({'success': False, 'message': 'API key required'})
        
        # Test the key
        try:
            from src.rewriters.gemini_rewriter import GeminiRewriter
            rewriter = GeminiRewriter(api_key)
            is_valid, message = rewriter.validate_api_key()
            return jsonify({'success': is_valid, 'message': message})
        except ImportError:
            return jsonify({'success': False, 'message': 'Gemini package not installed. Run: pip install google-generativeai'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get processing status"""
    return jsonify(processing_status)


def process_pdf_async(pdf_path: str, word_limit: int, processing_mode: str):
    """Process PDF in background thread"""
    global processing_status
    
    try:
        processing_status['is_processing'] = True
        processing_status['progress'] = 0
        processing_status['status_message'] = 'Starting processing...'
        processing_status['error'] = None
        processing_status['output_file'] = None
        
        # Create processor
        processor = NovelProcessor(config_manager)
        
        # Progress callback
        def progress_callback(current, total, message):
            processing_status['progress'] = int((current / total) * 100) if total > 0 else 0
            processing_status['status_message'] = message
            
            # Update stats if available
            if hasattr(processor, 'results'):
                summary = processor.get_summary()
                processing_status['stats'] = summary
        
        # Process PDF
        results = processor.process_pdf(
            pdf_path,
            word_limit=word_limit,
            processing_mode=processing_mode,
            progress_callback=progress_callback
        )
        
        # Generate output files
        processing_status['status_message'] = 'Generating output files...'
        processing_status['progress'] = 95
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # Save to CSV
        csv_path = os.path.join(app.config['OUTPUT_FOLDER'], f'{base_name}_{timestamp}.csv')
        processor.save_to_csv(csv_path)
        
        # Save to Excel
        excel_path = os.path.join(app.config['OUTPUT_FOLDER'], f'{base_name}_{timestamp}.xlsx')
        processor.save_to_excel(excel_path)
        
        # Save to Google Sheets
        processing_status['status_message'] = 'Creating Google Spreadsheet...'
        processing_status['progress'] = 97
        
        try:
            credentials_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
            token_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'token.json')
            
            sheets_result = processor.save_to_google_sheets(
                title=f'{base_name}_{timestamp}',
                credentials_path=credentials_path,
                token_path=token_path
            )
            
            processing_status['google_sheets_url'] = sheets_result['spreadsheet_url']
            processing_status['google_sheets_id'] = sheets_result['spreadsheet_id']
            processing_status['status_message'] = 'Google Spreadsheet created successfully!'
        except Exception as e:
            print(f"Google Sheets error: {str(e)}")
            processing_status['google_sheets_error'] = str(e)
            processing_status['status_message'] = 'Local files created (Google Sheets failed)'
        
        # Get final summary
        summary = processor.get_summary()
        processing_status['stats'] = summary
        processing_status['output_file'] = excel_path
        processing_status['csv_file'] = csv_path
        
        processing_status['progress'] = 100
        processing_status['status_message'] = 'Processing complete!'
        processing_status['is_processing'] = False
    
    except Exception as e:
        processing_status['error'] = str(e)
        processing_status['is_processing'] = False
        processing_status['status_message'] = f'Error: {str(e)}'
        print(f"Processing error: {str(e)}")
        import traceback
        traceback.print_exc()


@app.route('/api/process', methods=['POST'])
def process_pdf():
    """Start PDF processing"""
    global processing_status
    
    if processing_status['is_processing']:
        return jsonify({'success': False, 'error': 'Processing already in progress'}), 400
    
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Only PDF files are supported'}), 400
        
        # Get parameters
        word_limit = int(request.form.get('word_limit', config_manager.get_word_limit()))
        processing_mode = request.form.get('processing_mode', config_manager.get_processing_mode())
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Start processing in background
        thread = threading.Thread(
            target=process_pdf_async,
            args=(filepath, word_limit, processing_mode)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': 'Processing started'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/download/<path:filename>')
def download_file(filename):
    """Download output file"""
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404


if __name__ == '__main__':
    print("=" * 60)
    print("French Novel Processor - Web Interface")
    print("=" * 60)
    print("\nStarting server...")
    print("Open your browser to: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
