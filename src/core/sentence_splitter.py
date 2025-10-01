"""
Sentence Splitter Module
Handles both AI-powered rewriting and legacy mechanical chunking
"""

import re
import logging
from typing import List, Tuple, Optional
from enum import Enum
from src.rewriters.ai_rewriter import AIRewriter
from src.utils.validator import SentenceValidator
from src.utils.text_cleaner import clean_text_for_ai

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    """Processing mode enumeration"""
    AI_REWRITE = "ai_rewrite"
    MECHANICAL_CHUNKING = "mechanical_chunking"


class SentenceResult:
    """Result of processing a single sentence"""
    
    def __init__(self, original: str, output_sentences: List[str], 
                 method: str, word_count: int, success: bool = True, 
                 error: str = None):
        self.original = original
        self.output_sentences = output_sentences
        self.method = method  # "Direct", "AI-Rewritten", "Mechanical-Chunked", "Failed"
        self.word_count = word_count
        self.success = success
        self.error = error


class SentenceSplitter:
    """Handles sentence splitting with AI rewriting or mechanical chunking"""
    
    def __init__(self, word_limit: int = 8, mode: ProcessingMode = ProcessingMode.AI_REWRITE,
                 api_key: Optional[str] = None, use_gemini: bool = False):
        """
        Initialize sentence splitter
        
        Args:
            word_limit: Maximum words per sentence
            mode: Processing mode (AI or mechanical)
            api_key: API key (OpenAI or Gemini, required for AI mode)
            use_gemini: If True, use Gemini instead of OpenAI (development only)
        """
        self.word_limit = word_limit
        self.mode = mode
        self.validator = SentenceValidator(word_limit)
        self.use_gemini = use_gemini
        
        # Initialize AI rewriter if in AI mode
        self.ai_rewriter = None
        if mode == ProcessingMode.AI_REWRITE:
            if not api_key:
                raise ValueError("API key required for AI rewriting mode")
            
            # Smart selection: Gemini (dev) or OpenAI (production)
            if use_gemini:
                from src.rewriters.gemini_rewriter import GeminiRewriter
                self.ai_rewriter = GeminiRewriter(api_key, word_limit)
            else:
                self.ai_rewriter = AIRewriter(api_key, word_limit)
        
        # Statistics
        self.stats = {
            'total_sentences': 0,
            'direct_sentences': 0,
            'ai_rewritten': 0,
            'mechanical_chunked': 0,
            'failed': 0,
            'api_calls': 0
        }
        # Live results list so callers can observe progress incrementally
        self.results: List[SentenceResult] = []
    
    def count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    def extract_sentences(self, text: str) -> List[str]:
        """
        Extract sentences from text
        
        Args:
            text: Text to extract sentences from
            
        Returns:
            List of sentences
        """
        # Split on sentence-ending punctuation
        # Handle French quotes and special cases
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-ZÀÂÄÇÉÈÊËÎÏÔÙÛÜŸÆŒ])', text)
        
        # Clean up
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def mechanical_chunk(self, sentence: str) -> List[str]:
        """
        Split sentence using legacy mechanical chunking
        
        Args:
            sentence: Sentence to chunk
            
        Returns:
            List of chunks
        """
        words = sentence.split()
        chunks = []
        
        for i in range(0, len(words), self.word_limit):
            chunk = ' '.join(words[i:i + self.word_limit])
            chunks.append(chunk)
        
        return chunks
    
    def process_sentence(self, sentence: str) -> SentenceResult:
        """
        Process a single sentence
        
        Args:
            sentence: Sentence to process
            
        Returns:
            SentenceResult object
        """
        self.stats['total_sentences'] += 1
        word_count = self.count_words(sentence)
        
        # If sentence is within limit, pass through directly
        if word_count <= self.word_limit:
            self.stats['direct_sentences'] += 1
            return SentenceResult(
                original=sentence,
                output_sentences=[sentence],
                method="Direct",
                word_count=word_count,
                success=True
            )
        
        # Sentence exceeds limit - needs processing
        
        # AI Rewriting Mode
        if self.mode == ProcessingMode.AI_REWRITE and self.ai_rewriter:
            try:
                # Try AI rewriting
                rewritten = self.ai_rewriter.rewrite_sentence(sentence)
                self.stats['api_calls'] += 1
                
                # Validate the rewrite
                is_valid, error_msg, details = self.validator.validate_rewrite(
                    sentence, rewritten
                )
                
                if is_valid:
                    self.stats['ai_rewritten'] += 1
                    return SentenceResult(
                        original=sentence,
                        output_sentences=rewritten,
                        method="AI-Rewritten",
                        word_count=word_count,
                        success=True
                    )
                else:
                    # Validation failed - fall back to mechanical chunking
                    logger.warning(f"AI rewrite validation failed: {error_msg}")
                    logger.info("Falling back to mechanical chunking")
                    chunks = self.mechanical_chunk(sentence)
                    self.stats['mechanical_chunked'] += 1
                    return SentenceResult(
                        original=sentence,
                        output_sentences=chunks,
                        method="Mechanical-Chunked (AI validation failed)",
                        word_count=word_count,
                        success=True,
                        error=error_msg
                    )
                    
            except Exception as e:
                # AI rewriting failed - fall back to mechanical chunking
                logger.error(f"AI rewriting failed: {str(e)}")
                logger.info("Falling back to mechanical chunking")
                chunks = self.mechanical_chunk(sentence)
                self.stats['mechanical_chunked'] += 1
                return SentenceResult(
                    original=sentence,
                    output_sentences=chunks,
                    method="Mechanical-Chunked (AI failed)",
                    word_count=word_count,
                    success=True,
                    error=str(e)
                )
        
        # Mechanical Chunking Mode (or fallback)
        else:
            chunks = self.mechanical_chunk(sentence)
            self.stats['mechanical_chunked'] += 1
            return SentenceResult(
                original=sentence,
                output_sentences=chunks,
                method="Mechanical-Chunked",
                word_count=word_count,
                success=True
            )
    
    def _process_text_batch(self, sentences: List[str], progress_callback=None):
        """
        Process text using batch AI rewriting for better performance
        
        Args:
            sentences: List of sentences to process
            progress_callback: Optional callback function
        """
        batch_size = 20  # Process 20 sentences per API call (aggressively optimized)
        i = 0
        total = len(sentences)
        
        logger.info(f"Starting batch processing: {total} sentences, batch_size={batch_size}")
        
        while i < total:
            # Collect sentences for this batch
            batch_sentences = []
            batch_indices = []
            
            for j in range(batch_size):
                if i + j >= total:
                    break
                    
                sentence = sentences[i + j]
                word_count = self.count_words(sentence)
                
                # Check if sentence needs processing
                if word_count <= self.word_limit:
                    # Direct pass-through
                    self.stats['total_sentences'] += 1
                    self.stats['direct_sentences'] += 1
                    result = SentenceResult(
                        original=sentence,
                        output_sentences=[sentence],
                        method="Direct",
                        word_count=word_count,
                        success=True
                    )
                    self.results.append(result)
                    
                    if progress_callback:
                        progress_callback(i + j + 1, total, sentence)
                        try:
                            progress_callback(i + j + 1, total, {'done': True, 'index': i + j + 1})
                        except Exception:
                            pass
                            
                elif word_count > 25:  # Skip very long sentences (likely to fail validation)
                    # Use mechanical chunking directly
                    self.stats['total_sentences'] += 1
                    self.stats['mechanical_chunked'] += 1
                    chunks = self.mechanical_chunk(sentence)
                    result = SentenceResult(
                        original=sentence,
                        output_sentences=chunks,
                        method="Mechanical-Chunked (too long for AI)",
                        word_count=word_count,
                        success=True
                    )
                    self.results.append(result)
                    
                    if progress_callback:
                        progress_callback(i + j + 1, total, sentence)
                        try:
                            progress_callback(i + j + 1, total, {'done': True, 'index': i + j + 1})
                        except Exception:
                            pass
                else:
                    # Add to batch for AI rewriting
                    batch_sentences.append(sentence)
                    batch_indices.append(i + j)
            
            # Process the batch with AI if we have any sentences
            if batch_sentences:
                try:
                    # Call batch rewrite
                    logger.info(f"Processing batch of {len(batch_sentences)} sentences (batch #{self.stats['api_calls']+1})")
                    rewritten_dict = self.ai_rewriter.rewrite_batch(batch_sentences)
                    self.stats['api_calls'] += 1
                    logger.info(f"Batch processed successfully, got {len(rewritten_dict)} results")
                    
                    # Process each result
                    for idx, orig_sentence in enumerate(batch_sentences):
                        self.stats['total_sentences'] += 1
                        word_count = self.count_words(orig_sentence)
                        actual_idx = batch_indices[idx]
                        
                        # Get rewritten sentences from dict
                        rewritten = rewritten_dict.get(orig_sentence, [])
                        
                        if not rewritten:
                            # No result from AI - fall back to mechanical chunking
                            logger.warning(f"No AI result for sentence: {orig_sentence[:50]}...")
                            chunks = self.mechanical_chunk(orig_sentence)
                            self.stats['mechanical_chunked'] += 1
                            result = SentenceResult(
                                original=orig_sentence,
                                output_sentences=chunks,
                                method="Mechanical-Chunked (AI no result)",
                                word_count=word_count,
                                success=True,
                                error="No AI result"
                            )
                        else:
                            # Validate the rewrite
                            is_valid, error_msg, details = self.validator.validate_rewrite(
                                orig_sentence, rewritten
                            )
                            
                            if is_valid:
                                self.stats['ai_rewritten'] += 1
                                result = SentenceResult(
                                    original=orig_sentence,
                                    output_sentences=rewritten,
                                    method="AI-Rewritten",
                                    word_count=word_count,
                                    success=True
                                )
                            else:
                                # Validation failed - fall back to mechanical chunking
                                logger.warning(f"AI rewrite validation failed: {error_msg}")
                                chunks = self.mechanical_chunk(orig_sentence)
                                self.stats['mechanical_chunked'] += 1
                                result = SentenceResult(
                                    original=orig_sentence,
                                    output_sentences=chunks,
                                    method="Mechanical-Chunked (AI validation failed)",
                                    word_count=word_count,
                                    success=True,
                                    error=error_msg
                                )
                        
                        self.results.append(result)
                        
                        if progress_callback:
                            progress_callback(actual_idx + 1, total, orig_sentence)
                            try:
                                progress_callback(actual_idx + 1, total, {'done': True, 'index': actual_idx + 1})
                            except Exception:
                                pass
                                
                except Exception as e:
                    # Batch failed - fall back to mechanical chunking for all sentences in batch
                    logger.error(f"Batch AI rewriting failed: {str(e)}")
                    for idx, orig_sentence in enumerate(batch_sentences):
                        self.stats['total_sentences'] += 1
                        word_count = self.count_words(orig_sentence)
                        actual_idx = batch_indices[idx]
                        
                        chunks = self.mechanical_chunk(orig_sentence)
                        self.stats['mechanical_chunked'] += 1
                        result = SentenceResult(
                            original=orig_sentence,
                            output_sentences=chunks,
                            method="Mechanical-Chunked (AI batch failed)",
                            word_count=word_count,
                            success=True,
                            error=str(e)
                        )
                        self.results.append(result)
                        
                        if progress_callback:
                            progress_callback(actual_idx + 1, total, orig_sentence)
                            try:
                                progress_callback(actual_idx + 1, total, {'done': True, 'index': actual_idx + 1})
                            except Exception:
                                pass
            
            # Move to next batch
            i += batch_size
    
    def process_text(self, text: str, progress_callback=None) -> List[SentenceResult]:
        """
        Process entire text
        
        Args:
            text: Text to process
            progress_callback: Optional callback function(current, total, sentence)
            
        Returns:
            List of SentenceResult objects
        """
        # Pre-clean OCR artifacts to improve splitting and AI quality
        cleaned = clean_text_for_ai(text)
        sentences = self.extract_sentences(cleaned)

        # Reset live results for this run - clear the existing list so external
        # references (e.g. processor.results) remain valid.
        try:
            self.results.clear()
        except Exception:
            # If results is not yet a list, ensure it's an empty list
            self.results = []

        # Use batch processing for AI mode
        if self.mode == ProcessingMode.AI_REWRITE and self.ai_rewriter:
            self._process_text_batch(sentences, progress_callback)
        else:
            # Fallback to sentence-by-sentence processing
            for i, sentence in enumerate(sentences):
                if progress_callback:
                    progress_callback(i + 1, len(sentences), sentence)

                result = self.process_sentence(sentence)
                # Append to live results so external observers (processor) see updates
                self.results.append(result)

                # Notify again after appending so summaries computed from results include this sentence
                if progress_callback:
                    # Send a non-string payload so callers treat this as a status update
                    try:
                        progress_callback(i + 1, len(sentences), {'done': True, 'index': i + 1})
                    except Exception:
                        # Be tolerant of callbacks that expect strings
                        try:
                            progress_callback(i + 1, len(sentences), f'Done {i+1}')
                        except Exception:
                            pass

        return self.results
    
    def get_stats(self) -> dict:
        """Get processing statistics"""
        stats = self.stats.copy()
        
        # Add cost information if using AI
        if self.ai_rewriter:
            token_stats = self.ai_rewriter.get_token_stats()
            stats.update(token_stats)
        
        return stats
    
    def reset_stats(self):
        """Reset statistics counters"""
        self.stats = {
            'total_sentences': 0,
            'direct_sentences': 0,
            'ai_rewritten': 0,
            'mechanical_chunked': 0,
            'failed': 0,
            'api_calls': 0
        }
        
        if self.ai_rewriter:
            self.ai_rewriter.reset_token_count()
