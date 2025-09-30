"""
Main Processor Module
Orchestrates PDF processing, sentence splitting, and output generation
"""

import os
import time
from datetime import datetime
from typing import List, Optional, Callable
import pandas as pd
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import pytesseract
from src.core.sentence_splitter import SentenceSplitter, ProcessingMode, SentenceResult
from src.utils.config_manager import ConfigManager


class NovelProcessor:
    """Main processor for French novels"""
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize processor
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config = config_manager
        self.results: List[SentenceResult] = []
        self.processing_time = 0
        self.start_time = None
    
    def extract_text_from_pdf(self, pdf_path: str, progress_callback: Optional[Callable] = None) -> str:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            progress_callback: Optional callback for progress updates
            
        Returns:
            Extracted text
        """
        text = ""
        
        try:
            # Try direct text extraction first
            reader = PdfReader(pdf_path)
            num_pages = len(reader.pages)
            
            for i, page in enumerate(reader.pages):
                if progress_callback:
                    progress_callback(i + 1, num_pages, "Extracting text from PDF...")
                
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            # If text extraction yielded little content, try OCR
            if len(text.strip()) < 100:
                if progress_callback:
                    progress_callback(0, num_pages, "Text extraction insufficient, trying OCR...")
                
                text = self.extract_text_with_ocr(pdf_path, progress_callback)
        
        except Exception as e:
            print(f"Error extracting text: {str(e)}")
            # Try OCR as fallback
            if progress_callback:
                progress_callback(0, 0, "Falling back to OCR...")
            text = self.extract_text_with_ocr(pdf_path, progress_callback)
        
        return text
    
    def extract_text_with_ocr(self, pdf_path: str, progress_callback: Optional[Callable] = None) -> str:
        """
        Extract text using OCR
        
        Args:
            pdf_path: Path to PDF file
            progress_callback: Optional callback for progress updates
            
        Returns:
            Extracted text
        """
        text = ""
        
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            
            for i, image in enumerate(images):
                if progress_callback:
                    progress_callback(i + 1, len(images), "Running OCR...")
                
                # Run OCR with French language
                page_text = pytesseract.image_to_string(image, lang='fra')
                text += page_text + "\n"
        
        except Exception as e:
            print(f"OCR error: {str(e)}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
        
        return text
    
    def process_pdf(self, pdf_path: str, word_limit: Optional[int] = None, 
                   processing_mode: Optional[str] = None,
                   progress_callback: Optional[Callable] = None) -> List[SentenceResult]:
        """
        Process a PDF file
        
        Args:
            pdf_path: Path to PDF file
            word_limit: Word limit per sentence (uses config default if None)
            processing_mode: Processing mode (uses config default if None)
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of SentenceResult objects
        """
        self.start_time = time.time()
        
        # Get settings
        if word_limit is None:
            word_limit = self.config.get_word_limit()
        
        if processing_mode is None:
            processing_mode = self.config.get_processing_mode()
        
        # Extract text from PDF
        if progress_callback:
            progress_callback(0, 100, "Extracting text from PDF...")
        
        text = self.extract_text_from_pdf(pdf_path, progress_callback)
        
        if not text or len(text.strip()) < 10:
            raise Exception("No text extracted from PDF")
        
        # Initialize sentence splitter
        mode = ProcessingMode.AI_REWRITE if processing_mode == 'ai_rewrite' else ProcessingMode.MECHANICAL_CHUNKING
        
        # Smart API selection: Gemini (dev) or OpenAI (production)
        api_key = None
        use_gemini = False
        if mode == ProcessingMode.AI_REWRITE:
            if self.config.should_use_gemini():
                api_key = self.config.get_gemini_api_key()
                use_gemini = True
                if progress_callback:
                    progress_callback(45, 100, "Using Gemini AI (Development Mode)...")
            else:
                api_key = self.config.get_api_key()
                if progress_callback:
                    progress_callback(45, 100, "Using OpenAI GPT-4o-mini...")
            
            if not api_key:
                raise Exception("API key required for AI rewriting mode. Please configure it in settings.")
        
        splitter = SentenceSplitter(word_limit=word_limit, mode=mode, api_key=api_key, use_gemini=use_gemini)
        
        # Process sentences
        if progress_callback:
            progress_callback(50, 100, "Processing sentences...")
        
        self.results = splitter.process_text(text, progress_callback)
        
        self.processing_time = time.time() - self.start_time
        
        return self.results
    
    def generate_dataframe(self) -> pd.DataFrame:
        """
        Generate pandas DataFrame from results
        
        Returns:
            DataFrame with processed sentences
        """
        rows = []
        row_num = 1
        
        show_original = self.config.get_show_original()
        
        for result in self.results:
            for sentence in result.output_sentences:
                row = {
                    'Row': row_num,
                    'Sentence': sentence,
                    'Word_Count': len(sentence.split())
                }
                
                if show_original and result.method != "Direct":
                    row['Original'] = result.original
                    row['Method'] = result.method
                else:
                    row['Original'] = ''
                    row['Method'] = result.method if result.method != "Direct" else ''
                
                rows.append(row)
                row_num += 1
        
        # Create DataFrame
        columns = ['Row', 'Sentence']
        if show_original:
            columns.extend(['Original', 'Method'])
        columns.append('Word_Count')
        
        df = pd.DataFrame(rows)
        
        # Reorder columns
        existing_cols = [col for col in columns if col in df.columns]
        df = df[existing_cols]
        
        return df
    
    def generate_processing_log(self) -> pd.DataFrame:
        """
        Generate processing log DataFrame
        
        Returns:
            DataFrame with processing details
        """
        log_rows = []
        
        for i, result in enumerate(self.results):
            if result.method != "Direct":
                log_rows.append({
                    'Sentence_Number': i + 1,
                    'Original': result.original,
                    'Original_Word_Count': result.word_count,
                    'Method': result.method,
                    'Output_Sentences': ' | '.join(result.output_sentences),
                    'Success': result.success,
                    'Error': result.error or ''
                })
        
        return pd.DataFrame(log_rows)
    
    def save_to_csv(self, output_path: str):
        """
        Save results to CSV file
        
        Args:
            output_path: Path to output CSV file
        """
        df = self.generate_dataframe()
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        # Save processing log if enabled
        if self.config.get_generate_log():
            log_df = self.generate_processing_log()
            if not log_df.empty:
                log_path = output_path.replace('.csv', '_log.csv')
                log_df.to_csv(log_path, index=False, encoding='utf-8-sig')
    
    def save_to_excel(self, output_path: str):
        """
        Save results to Excel file
        
        Args:
            output_path: Path to output Excel file
        """
        df = self.generate_dataframe()
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Sentences', index=False)
            
            # Add processing log if enabled
            if self.config.get_generate_log():
                log_df = self.generate_processing_log()
                if not log_df.empty:
                    log_df.to_excel(writer, sheet_name='Processing Log', index=False)
    
    def get_summary(self) -> dict:
        """
        Get processing summary
        
        Returns:
            Dictionary with summary statistics
        """
        total_sentences = len(self.results)
        direct = sum(1 for r in self.results if r.method == "Direct")
        ai_rewritten = sum(1 for r in self.results if "AI-Rewritten" in r.method)
        mechanical = sum(1 for r in self.results if "Mechanical" in r.method)
        failed = sum(1 for r in self.results if not r.success)
        
        total_output_sentences = sum(len(r.output_sentences) for r in self.results)
        
        summary = {
            'total_input_sentences': total_sentences,
            'total_output_sentences': total_output_sentences,
            'direct_sentences': direct,
            'ai_rewritten': ai_rewritten,
            'mechanical_chunked': mechanical,
            'failed': failed,
            'processing_time': self.processing_time
        }
        
        return summary
