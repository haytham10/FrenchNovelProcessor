"""
Sentence Splitter Module
Handles both AI-powered rewriting and legacy mechanical chunking
"""

import re
import logging
from typing import List, Optional, Dict
from enum import Enum
from src.rewriters.ai_rewriter import AIRewriter
from src.utils.validator import SentenceValidator
from src.utils.text_cleaner import clean_text_for_ai, SENTENCE_BREAK_TOKEN

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
        self.max_ai_sentence_words = 500  # AI can handle long segments - let it work!
        
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

        # Verb detection cache
        self._verb_pattern = re.compile(
            r"\b(" + "|".join([
                "suis", "es", "est", "sommes", "êtes", "sont",
                "étais", "était", "étions", "étiez", "étaient",
                "serai", "sera", "seront",
                "ai", "as", "a", "avons", "avez", "ont",
                "vais", "vas", "va", "allons", "allez", "vont",
                "fais", "fait", "faisons", "faites", "font",
                "peux", "peut", "pouvons", "pouvez", "peuvent",
                "veux", "veut", "voulons", "voulez", "veulent",
                "dois", "doit", "devons", "devez", "doivent",
                "viens", "vient", "venons", "venez", "viennent",
                "dis", "dit", "disons", "dites", "disent",
                "vois", "voit", "voyons", "voyez", "voient",
                "prends", "prend", "prenons", "prenez", "prennent",
                "mets", "met", "mettons", "mettez", "mettent",
                "sais", "sait", "savons", "savez", "savent",
                "crois", "croit", "croyons", "croyez", "croient",
                "pense", "penses", "pensons", "pensez", "pensent",
                "aime", "aimes", "aimons", "aimez", "aiment",
                "regarde", "regardes", "regardons", "regardez", "regardent",
                "joue", "joues", "jouons", "jouez", "jouent",
                "vit", "vis", "vivons", "vivent",
                "sent", "sens", "sentons", "sentez", "sentent"
            ]) + r")\b",
            flags=re.IGNORECASE
        )
    
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
        segments = [seg.strip() for seg in text.split(SENTENCE_BREAK_TOKEN) if seg.strip()]
        
        # For AI mode: return segments as-is (let AI split them naturally - Phase 1)
        if self.mode == ProcessingMode.AI_REWRITE and self.ai_rewriter:
            return [re.sub(r"\s+", " ", seg).strip() for seg in segments if seg.strip()]
        
        # For Mechanical mode: pre-split into sentences
        sentences: List[str] = []

        split_pattern = re.compile(
            r'(?<=[.!?])\s+(?=[A-ZÀÂÄÇÉÈÊËÎÏÔÙÛÜŸÆŒ"«“])'
        )

        for segment in segments:
            normalized = re.sub(r"\s+", " ", segment).strip()
            if not normalized:
                continue

            parts = split_pattern.split(normalized)
            for part in parts:
                candidate = part.strip()
                if candidate:
                    sentences.append(candidate)

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

    def _create_result(
        self,
        original: str,
        output_sentences: List[str],
        method: str,
        word_count: int,
        success: bool = True,
        error: Optional[str] = None
    ) -> SentenceResult:
        return SentenceResult(
            original=original,
            output_sentences=output_sentences,
            method=method,
            word_count=word_count,
            success=success,
            error=error
        )

    def _direct_result(self, sentence: str, word_count: int) -> SentenceResult:
        self.stats['direct_sentences'] += 1
        return self._create_result(sentence, [sentence], "Direct", word_count)

    def _mechanical_result(
        self,
        sentence: str,
        word_count: int,
        method: str = "Mechanical-Chunked",
        error: Optional[str] = None
    ) -> SentenceResult:
        chunks = self.mechanical_chunk(sentence)
        self.stats['mechanical_chunked'] += 1
        return self._create_result(sentence, chunks, method, word_count, success=True, error=error)

    def _run_ai_pipeline(
        self,
        sentence: str,
        word_count: int,
        *,
        initial_rewrite: Optional[List[str]] = None,
        initial_method: str = "AI-Rewritten",
        initial_call_counted: bool = False,
        fallback_label: str = "Mechanical-Chunked (AI validation failed)"
    ) -> SentenceResult:
        try:
            if initial_rewrite is None:
                self.stats['api_calls'] += 1
                candidate = self.ai_rewriter.rewrite_sentence(sentence)
            else:
                candidate = initial_rewrite
                if not initial_call_counted:
                    self.stats['api_calls'] += 1
        except Exception as exc:
            logger.error(f"AI rewriting failed: {exc}")
            return self._mechanical_result(
                sentence,
                word_count,
                method="Mechanical-Chunked (AI failed)",
                error=str(exc)
            )

        reason = None
        if candidate:
            # TWO-PHASE APPROACH:
            # Phase 1 (AI): Already done - AI split paragraph into natural sentences
            # Phase 2 (Local): Only apply repair if validation fails
            
            # First, try to validate AI output as-is
            is_valid, error_msg, details = self.validator.validate_rewrite(sentence, candidate)
            if is_valid:
                self.stats['ai_rewritten'] += 1
                return self._create_result(sentence, candidate, "AI-Rewritten", word_count)
            
            # Only apply repair if word count exceeded
            if "Word count exceeded" in (error_msg or ""):
                repaired = self._local_repair_overlimit(candidate, self.word_limit)
                repaired_valid, repaired_msg, _ = self.validator.validate_rewrite(sentence, repaired)
                if repaired_valid:
                    self.stats['ai_rewritten'] += 1
                    return self._create_result(sentence, repaired, "AI+LocalRepair", word_count)
                reason = repaired_msg or "Validation failed after repair"
            else:
                reason = error_msg or "Validation failed"
        else:
            reason = "No AI result"

        return self._mechanical_result(
            sentence,
            word_count,
            method=fallback_label,
            error=reason
        )

    def _local_repair_overlimit(self, ai_out: List[str], limit: int) -> List[str]:
        """
        MINIMAL repair: Only split sentences that actually exceed limit.
        Trust AI output - don't re-split good sentences!
        Removes page numbers at end.
        """
        repaired: List[str] = []
        # Precompiled breakpoint pattern for speed
        breaker = re.compile(r"[,;:]|\s(?:et|mais|ou|car|que|qui|quand|donc|ainsi|avec|dans|pour|par)\s", re.IGNORECASE)
        
        for s in ai_out:
            s = re.sub(r"\s+", " ", s).strip()
            if not s:
                continue
            
            # Remove trailing punctuation and page numbers
            s = s.rstrip('.!?')
            words = s.split()
            
            # Remove page number at end (typically 1-3 digit number)
            if words and words[-1].isdigit():
                words = words[:-1]
            
            if not words:
                continue
                
            wc = len(words)
            
            # Fast path: already compliant with the word limit
            if wc <= limit:
                repaired.append(' '.join(words))
                continue
            
            # Need to split - try smart split on natural breakpoints
            parts = breaker.split(s)
            if len(parts) > 1:
                # Greedy bin packing to limit
                chunk = []
                chunk_len = 0
                for part in parts:
                    part = part.strip().rstrip('.!?,;:—–-')
                    if not part:
                        continue
                    pw = part.split()
                    if chunk_len + len(pw) <= limit:
                        chunk.extend(pw)
                        chunk_len += len(pw)
                    else:
                        if chunk:
                            repaired.append(' '.join(chunk))
                        # Handle oversized single part
                        if len(pw) > limit:
                            for i in range(0, len(pw), limit):
                                repaired.append(' '.join(pw[i:i+limit]))
                            chunk = []
                            chunk_len = 0
                        else:
                            chunk = pw
                            chunk_len = len(pw)
                if chunk:
                    repaired.append(' '.join(chunk))
            else:
                # No natural breakpoints: hard split by word windows
                for i in range(0, wc, limit):
                    repaired.append(' '.join(words[i:i+limit]))
        
        return repaired

    def _process_sentence_pipeline(
        self,
        sentence: str,
        *,
        word_count: Optional[int] = None,
        initial_rewrite: Optional[List[str]] = None,
        initial_call_counted: bool = True,
        force_mechanical: bool = False,
        mechanical_method: Optional[str] = None,
        mechanical_reason: Optional[str] = None,
        ai_fallback_label: Optional[str] = None
    ) -> SentenceResult:
        if word_count is None:
            word_count = self.count_words(sentence)

        self.stats['total_sentences'] += 1

        if (
            word_count <= self.word_limit
            and not force_mechanical
            and self._looks_like_sentence(sentence)
        ):
            return self._direct_result(sentence, word_count)

        if self.mode != ProcessingMode.AI_REWRITE or not self.ai_rewriter or force_mechanical:
            return self._mechanical_result(
                sentence,
                word_count,
                method=mechanical_method or "Mechanical-Chunked",
                error=mechanical_reason
            )

        return self._run_ai_pipeline(
            sentence,
            word_count,
            initial_rewrite=initial_rewrite,
            initial_method="AI-Rewritten",
            initial_call_counted=initial_call_counted,
            fallback_label=ai_fallback_label or mechanical_method or "Mechanical-Chunked (AI validation failed)"
        )

    def _notify_progress(self, progress_callback, current: int, total: int, payload) -> None:
        if progress_callback:
            try:
                progress_callback(current, total, payload)
            except Exception:
                pass

    def _looks_like_sentence(self, text: str) -> bool:
        if not text:
            return False

        stripped = text.strip()
        if not stripped:
            return False

        if stripped.isdigit():
            return False

        words = [w for w in re.findall(r"[\wà-öø-ÿÀ-ÖØ-ßœŒæÆ']+", stripped)]
        if len(words) < 2:
            return False

        if not re.search(r"[.!?…]\"?$", stripped):
            return False

        if self._verb_pattern.search(stripped.lower()):
            return True

        return False
    
    def process_sentence(self, sentence: str) -> SentenceResult:
        """
        Process a single sentence according to the algorithm:
        1. If sentence has word_limit words or fewer: add directly to output
        2. If sentence is longer: rewrite into multiple sentences that meet the criterion
           - Each new sentence must be ≤ word_limit words
           - Use as many original words as possible
           - Retain overall meaning
        
        Args:
            sentence: Sentence to process
            
        Returns:
            SentenceResult object
        """
        word_count = self.count_words(sentence)

        if word_count <= self.word_limit:
            return self._process_sentence_pipeline(
                sentence,
                word_count=word_count,
                initial_call_counted=False
            )

        if self.mode != ProcessingMode.AI_REWRITE or not self.ai_rewriter:
            return self._process_sentence_pipeline(
                sentence,
                word_count=word_count,
                force_mechanical=True,
                mechanical_method="Mechanical-Chunked"
            )

        if word_count > self.max_ai_sentence_words:
            reason = (
                f"Sentence length {word_count} exceeds AI threshold {self.max_ai_sentence_words}"
            )
            return self._process_sentence_pipeline(
                sentence,
                word_count=word_count,
                force_mechanical=True,
                mechanical_method="Mechanical-Chunked (too long for AI)",
                mechanical_reason=reason
            )

        return self._process_sentence_pipeline(
            sentence,
            word_count=word_count,
            initial_call_counted=False
        )
    
    def _process_text_batch(self, sentences: List[str], progress_callback=None):
        """
        Process text using batch AI rewriting for better performance
        
        Args:
            sentences: List of sentences to process
            progress_callback: Optional callback function
        """
        batch_size = 50  # Larger batches for maximum speed
        total = len(sentences)

        i = 0
        while i < total:
            batch_sentences: List[str] = []
            batch_indices: List[int] = []
            batch_word_counts: List[int] = []

            for j in range(batch_size):
                idx = i + j
                if idx >= total:
                    break

                sentence = sentences[idx]
                word_count = self.count_words(sentence)

                if word_count <= self.word_limit:
                    result = self._process_sentence_pipeline(
                        sentence,
                        word_count=word_count,
                        initial_call_counted=False
                    )
                    self.results.append(result)
                    self._notify_progress(progress_callback, idx + 1, total, sentence)
                elif word_count > self.max_ai_sentence_words:
                    reason = (
                        f"Sentence length {word_count} exceeds AI threshold {self.max_ai_sentence_words}"
                    )
                    result = self._process_sentence_pipeline(
                        sentence,
                        word_count=word_count,
                        force_mechanical=True,
                        mechanical_method="Mechanical-Chunked (too long for AI)",
                        mechanical_reason=reason
                    )
                    self.results.append(result)
                    self._notify_progress(progress_callback, idx + 1, total, sentence)
                else:
                    batch_sentences.append(sentence)
                    batch_indices.append(idx)
                    batch_word_counts.append(word_count)

            if batch_sentences:
                batch_error = None
                rewritten_dict: Dict[str, List[str]] = {}
                try:
                    rewritten_dict = self.ai_rewriter.rewrite_batch(batch_sentences)
                    self.stats['api_calls'] += 1
                except Exception as exc:
                    batch_error = str(exc)
                    logger.error(f"Batch AI rewriting failed: {batch_error}")

                for local_idx, orig_sentence in enumerate(batch_sentences):
                    idx = batch_indices[local_idx]
                    word_count = batch_word_counts[local_idx]

                    if batch_error:
                        result = self._process_sentence_pipeline(
                            orig_sentence,
                            word_count=word_count,
                            force_mechanical=True,
                            mechanical_method="Mechanical-Chunked (AI batch failed)",
                            mechanical_reason=batch_error
                        )
                    else:
                        rewritten = rewritten_dict.get(orig_sentence)
                        fallback_label = "Mechanical-Chunked (AI validation failed)"
                        if not rewritten:
                            fallback_label = "Mechanical-Chunked (AI no result)"
                            rewritten = rewritten or []

                        result = self._process_sentence_pipeline(
                            orig_sentence,
                            word_count=word_count,
                            initial_rewrite=rewritten,
                            initial_call_counted=True,
                            ai_fallback_label=fallback_label
                        )

                    self.results.append(result)
                    self._notify_progress(progress_callback, idx + 1, total, orig_sentence)

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
                result = self.process_sentence(sentence)
                # Append to live results so external observers (processor) see updates
                self.results.append(result)

                self._notify_progress(progress_callback, i + 1, len(sentences), sentence)

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
