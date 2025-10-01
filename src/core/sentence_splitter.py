"""
Sentence Splitter Module
Handles both AI-powered rewriting and legacy mechanical chunking
Optimized with adaptive batching and caching for improved performance
"""

import re
import logging
from typing import List, Tuple, Optional
from enum import Enum
from src.rewriters.ai_rewriter import AIRewriter
from src.utils.validator import SentenceValidator
from src.utils.text_cleaner import clean_text_for_ai
from src.utils.sentence_cache import SentenceCache

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
            'api_calls': 0,
            'cache_hits': 0
        }
        # Live results list so callers can observe progress incrementally
        self.results: List[SentenceResult] = []
        
        # Initialize cache for AI mode to improve performance
        self.cache = SentenceCache(max_size=500) if mode == ProcessingMode.AI_REWRITE else None
    
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
    
    def _get_optimal_batch_size(self, avg_word_count: int) -> int:
        """
        Determine optimal batch size based on sentence complexity
        
        Args:
            avg_word_count: Average word count of sentences in batch
            
        Returns:
            Optimal batch size
        """
        if avg_word_count <= 12:
            return 35  # Simple sentences: larger batches
        elif avg_word_count <= 18:
            return 25  # Medium sentences: standard batches
        else:
            return 15  # Complex sentences: smaller batches
    
    def _process_text_batch(self, sentences: List[str], progress_callback=None):
        """
        Process text using adaptive batch AI rewriting for optimal performance
        
        Args:
            sentences: List of sentences to process
            progress_callback: Optional callback function
        """
        i = 0
        total = len(sentences)
        
        logger.info(f"Starting adaptive batch processing: {total} sentences")
        
        while i < total:
            # Collect sentences for this batch (adaptive sizing)
            batch_sentences = []
            batch_indices = []
            batch_word_counts = []
            
            # First pass: determine batch composition
            temp_batch = []
            temp_indices = []
            j = 0
            max_look_ahead = 50  # Look ahead up to 50 sentences
            
            while j < max_look_ahead and (i + j) < total:
                sentence = sentences[i + j]
                word_count = self.count_words(sentence)
                
                # Quick categorization
                if word_count <= self.word_limit:
                    # Direct pass-through (handle immediately)
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
                            
                elif word_count > 30:  # Optimization: very long sentences use mechanical chunking
                    # Use mechanical chunking directly (faster, no API cost)
                    self.stats['total_sentences'] += 1
                    self.stats['mechanical_chunked'] += 1
                    chunks = self.mechanical_chunk(sentence)
                    result = SentenceResult(
                        original=sentence,
                        output_sentences=chunks,
                        method="Mechanical-Chunked (>30 words, optimized)",
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
                    # Check cache before adding to AI batch
                    if self.cache:
                        cached_result = self.cache.get(sentence)
                        if cached_result:
                            # Cache hit! Use cached rewrite
                            self.stats['total_sentences'] += 1
                            self.stats['ai_rewritten'] += 1
                            self.stats['cache_hits'] += 1
                            result = SentenceResult(
                                original=sentence,
                                output_sentences=cached_result,
                                method="AI-Rewritten (cached)",
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
                            
                            j += 1
                            continue
                    
                    # Add to batch for AI rewriting
                    temp_batch.append(sentence)
                    temp_indices.append(i + j)
                    batch_word_counts.append(word_count)
                
                j += 1
            
            # Determine optimal batch size based on complexity
            if temp_batch:
                avg_word_count = sum(batch_word_counts) / len(batch_word_counts)
                optimal_batch_size = self._get_optimal_batch_size(avg_word_count)
                
                # Take only optimal_batch_size sentences
                batch_sentences = temp_batch[:optimal_batch_size]
                batch_indices = temp_indices[:optimal_batch_size]
                
                logger.info(f"Batch composition: {len(batch_sentences)} sentences, "
                          f"avg {avg_word_count:.1f} words, batch_size={optimal_batch_size}")
            
            # Process the batch with AI if we have any sentences
            if batch_sentences:
                try:
                    # Call batch rewrite
                    logger.info(f"Processing AI batch of {len(batch_sentences)} sentences (call #{self.stats['api_calls']+1})")
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
                                # Cache successful rewrites for future use
                                if self.cache:
                                    self.cache.put(orig_sentence, rewritten)
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
            
            # Move to next position (account for sentences we just processed)
            i += j
    
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
        """Get processing statistics including cache performance"""
        stats = self.stats.copy()
        
        # Add cost information if using AI
        if self.ai_rewriter:
            token_stats = self.ai_rewriter.get_token_stats()
            stats.update(token_stats)
        
        # Add cache statistics if cache is enabled
        if self.cache:
            cache_stats = self.cache.get_stats()
            stats['cache_size'] = cache_stats['size']
            stats['cache_hit_rate'] = cache_stats['hit_rate']
        
        return stats
    
    def reset_stats(self):
        """Reset statistics counters"""
        self.stats = {
            'total_sentences': 0,
            'direct_sentences': 0,
            'ai_rewritten': 0,
            'mechanical_chunked': 0,
            'failed': 0,
            'api_calls': 0,
            'cache_hits': 0
        }
        
        if self.ai_rewriter:
            self.ai_rewriter.reset_token_count()
        
        if self.cache:
            self.cache.clear()
