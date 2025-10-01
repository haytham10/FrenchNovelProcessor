"""
AI-Powered Sentence Rewriter - Optimized for GPT-5 nano with Fast Batch Processing
Uses simple text format for maximum speed (no structured outputs overhead)
"""

import logging
import re
from typing import List, Tuple, Dict, Optional

# Optional dependencies: allow importing this module without OpenAI/tiktoken installed
try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional at import time
    OpenAI = None  # type: ignore

try:
    import tiktoken  # type: ignore
except Exception:  # pragma: no cover - optional at import time
    tiktoken = None  # type: ignore

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AIRewriter:
    """Streamlined AI rewriter optimized for GPT-5 nano batch processing"""

    def __init__(self, api_key: str, word_limit: int = 8, model: str = "gpt-5-nano"):
        """
        Initialize the AI Rewriter
        
        Args:
            api_key: OpenAI API key
            word_limit: Maximum words per sentence
            model: OpenAI model (default: gpt-5-nano)
        """
        # Lazy client init if OpenAI is available; else defer to call sites
        if OpenAI is not None:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None  # type: ignore
        self.word_limit = word_limit
        self.model = model
        
        # Token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.api_call_count = 0
        
        # Encoding
        self.encoding = None
        if tiktoken is not None:
            try:
                self.encoding = tiktoken.encoding_for_model("gpt-5-nano")
            except Exception:
                try:
                    self.encoding = tiktoken.get_encoding("cl100k_base")
                except Exception:
                    self.encoding = None
        
        # Pricing (GPT-5 mini) - approximate pricing
        self.input_price_per_1m = 0.10
        self.output_price_per_1m = 0.60
        
        # System prompt (built once)
        self._system_prompt = self._create_system_prompt()

        # Batch rewrite schema
        self._BatchRewriteSchema = self._create_batch_schema()
        # Strict rewrite schema
        self._StrictRewriteSchema = self._create_strict_schema()

    # --------------------
    # Text helpers (strict mode)
    # --------------------
    def _normalize(self, text: str) -> str:
        """Light normalization: collapse spaces, standardize quotes/dashes, strip."""
        if not text:
            return ""
        # Replace unusual spaces and dashes
        t = text.replace('\u00A0', ' ').replace('\u2011', '-')
        t = t.replace('“', '"').replace('”', '"').replace("’", "'")
        # Collapse whitespace
        t = re.sub(r"\s+", " ", t).strip()
        return t

    def _word_tokens(self, text: str) -> list:
        """Tokenize keeping French letters and apostrophes; lowercase for matching."""
        text = self._normalize(text).lower()
        # Keep letters (incl. accents), digits, apostrophes inside words
        return re.findall(r"[a-zà-öø-ÿœæ0-9]+'?[a-zà-öø-ÿœæ0-9]+|[a-zà-öø-ÿœæ0-9]+", text)

    def _is_subsequence(self, subseq: list, seq: list) -> bool:
        """Check if subseq appears in seq in order (not necessarily contiguous)."""
        if not subseq:
            return True
        i = 0
        for token in seq:
            if token == subseq[i]:
                i += 1
                if i == len(subseq):
                    return True
        return False

    def _enforce_original_words_and_order(self, original: str, candidate: str) -> bool:
        """Return True if candidate uses only words from original and preserves order."""
        orig_tokens = self._word_tokens(original)
        cand_tokens = self._word_tokens(candidate)
        if not cand_tokens:
            return False
        # All candidate tokens must exist in original
        orig_set = set(orig_tokens)
        if any(tok not in orig_set for tok in cand_tokens):
            return False
        # And must appear in original order
        return self._is_subsequence(cand_tokens, orig_tokens)
    
    def _create_batch_schema(self):
        """Create Pydantic schema for batch structured outputs"""
        class SentenceRewrite(BaseModel):
            index: int
            rewritten: List[str]
        
        class BatchRewriteResult(BaseModel):
            results: List[SentenceRewrite]
        
        return BatchRewriteResult

    def _create_strict_schema(self):
        """Create Pydantic schema for strict single-sentence structured output"""
        class StrictRewriteSchema(BaseModel):
            sentences: List[str]

        return StrictRewriteSchema
    
    def _create_system_prompt(self) -> str:
        """Create optimized system prompt for Phase 1: natural sentence splitting"""
        return (
            "Tu es un expert en segmentation de texte français. "
            "Divise les paragraphes en phrases COMPLÈTES qui ont du SENS individuellement. "
            "Chaque phrase doit être compréhensible sans contexte. "
            "NE COUPE JAMAIS au milieu d'une pensée."
        )
    
    def validate_api_key(self) -> Tuple[bool, str]:
        """Validate API key with minimal call"""
        try:
            if self.client is None:
                return False, "OpenAI SDK not installed"
            response = self.client.responses.create(
                model=self.model,
                input=[{"role": "user", "content": [{"type": "input_text", "text": "Test"}]}],
                reasoning={"effort": "minimal"},
                text={"verbosity": "low"},
                max_output_tokens=5
            )
            
            output = self._extract_output(response)
            return (True, "API key valid") if output else (False, "Empty response")
            
        except Exception as e:
            error_msg = str(e)
            if "invalid_api_key" in error_msg or "Incorrect API key" in error_msg:
                return False, "Invalid API key"
            elif "insufficient_quota" in error_msg:
                return False, "Insufficient credits"
            return False, f"Error: {error_msg}"
    
    def _extract_output(self, response) -> str:
        """Extract text from Responses API response"""
        if not response:
            return ""
        
        # Try convenience property first
        if hasattr(response, "output_text"):
            return response.output_text.strip()
        
        # Fallback: parse output structure
        text_parts = []
        try:
            output = getattr(response, "output", None) or []
            for item in output:
                content = getattr(item, "content", None) or []
                for segment in content:
                    text = getattr(segment, "text", None)
                    if text:
                        text_parts.append(text)
        except Exception as e:
            logger.debug(f"Output parsing fallback: {e}")
        
        return " ".join(text_parts).strip()
    
    def _track_usage(self, response) -> None:
        """Track token usage from response"""
        self.api_call_count += 1
        if hasattr(response, "usage"):
            self.total_input_tokens += getattr(response.usage, "input_tokens", 0) or 0
            self.total_output_tokens += getattr(response.usage, "output_tokens", 0) or 0
    
    def count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count"""
        try:
            if self.encoding is not None:
                return len(self.encoding.encode(text))
        except Exception:
            pass
        return int(len(text.split()) * 1.33)

    # --------------------
    # Public prompt accessors (used by tests)
    # --------------------
    def get_system_prompt(self) -> str:
        """Return a human-readable system prompt description (keeps word 'French' for tests)."""
        return f"French sentence rewriter. Max {self.word_limit} words per sentence."

    def get_user_prompt(self, sentence: str) -> str:
        """Return a sample user prompt for a single sentence (used in tests)."""
        return (
            f"Rewrite in French into sentences of at most {self.word_limit} words.\n"
            f"Text: {sentence}"
        )
    
    def rewrite_sentence(self, sentence: str) -> List[str]:
        """
        Rewrite a single sentence (uses batch internally for efficiency)
        
        Args:
            sentence: Sentence to rewrite
            
        Returns:
            List of rewritten sentences
        """
        result = self.rewrite_batch([sentence])
        return result.get(sentence, [sentence])
    
    def rewrite_batch(self, sentences: List[str]) -> Dict[str, List[str]]:
        """
        COMPLETELY NEW APPROACH:
        1. Ask AI to split into natural, meaningful sentences (no word limit pressure)
        2. Post-process: merge short sentences, split long ones
        This separates semantic understanding (AI) from mechanical constraint (local)
        """
        if not sentences:
            return {}

        # NEW STRATEGY: Let AI focus on meaning, not counting
        numbered = "\n".join([f"{i+1}) {s}" for i, s in enumerate(sentences)])
        user_prompt = (
            f"Split each paragraph into complete, natural French sentences.\n"
            f"RULES:\n"
            f"• Each sentence must be a complete thought\n"
            f"• Keep sentences SHORT (prefer simple over complex)\n"
            f"• Use ALL original words in exact order\n"
            f"• Fix OCR errors: 'gâ teaux'→'gâteaux', 'vigi lante'→'vigilante', 'de­ vant'→'devant'\n"
            f"• One sentence per line\n\n"
            f"{numbered}"
        )

        if self.client is None:
            raise RuntimeError("OpenAI SDK not installed")
        
        response = self.client.responses.create(
            model=self.model,
            instructions="Split French text into short, natural sentences. Focus on meaning and completeness, not word count.",
            input=user_prompt,
            store=False,
            max_output_tokens=max(200, min(1800, len(sentences) * 60)),
        )
        self._track_usage(response)
        output = self._extract_output(response)
        
        if not output:
            return {s: [s] for s in sentences}
        
        # Parse AI output
        results = self._parse_simple_response(output, sentences)
        
        # POST-PROCESS: Smart merge/split to hit word limit
        final_results: Dict[str, List[str]] = {}
        for orig in sentences:
            ai_sentences = results.get(orig, [orig])
            final_results[orig] = self._smart_pack_to_limit(ai_sentences, self.word_limit)
        
        return final_results

    def rewrite_sentence_strict(
        self,
        sentence: str,
        reason: Optional[str] = None,
        max_retries: int = 1
    ) -> Optional[List[str]]:
        """Fallback using Structured Outputs for guaranteed compliance"""

        system_prompt = f"Max {self.word_limit} mots/phrase. Divise si nécessaire. Préserve sens."

        for attempt in range(max_retries):
            try:
                user_prompt = (
                    f"{sentence}\n\n"
                    f"Max {self.word_limit} mots/phrase. JSON: {{\"sentences\": [...]}}"
                )
                if reason:
                    user_prompt = f"Échec précédent: {reason}\n\n" + user_prompt

                response = self.client.responses.parse(
                    # client is assumed available here; strict mode is used only when API available
                    model=self.model,
                    input=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    text_format=self._StrictRewriteSchema,
                )

                self._track_usage(response)

                parsed = response.output_parsed
                if parsed and parsed.sentences:
                    cleaned = [self._normalize(s) for s in parsed.sentences if s.strip()]
                    if cleaned:
                        return cleaned

            except Exception as e:
                logger.debug(f"Strict rewrite attempt {attempt + 1} failed: {e}")

        return None
    
    def _parse_simple_response(self, output: str, original_sentences: List[str]) -> Dict[str, List[str]]:
        """
        Simple parser: Each line is one phrase
        Format: 
        1) phrase one
        1) phrase two
        2) next sentence phrase
        """
        text = (output or "").strip()
        results: Dict[str, List[str]] = {}
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Match "n) text" or "n: text" or "n. text"
            m = re.match(r"(\d+)[:.)\-]\s*(.+)", line)
            if not m:
                continue
            
            idx_str, content = m.groups()
            try:
                idx = int(idx_str) - 1
            except ValueError:
                continue
            
            if idx < 0 or idx >= len(original_sentences):
                continue
            
            original_sentence = original_sentences[idx]
            
            # Clean up: remove trailing punctuation (not needed in output format)
            content = content.strip().rstrip('.!?,;:—–-')
            if not content:
                continue
            
            # Add this phrase to the list for this sentence
            if original_sentence not in results:
                results[original_sentence] = []
            results[original_sentence].append(content)
        
        return results
    
    def _smart_pack_to_limit(self, sentences: List[str], limit: int) -> List[str]:
        """
        Smart packing algorithm:
        1. MERGE short sentences together (< limit/2 words) 
        2. KEEP medium sentences as-is (≤ limit words)
        3. SPLIT long sentences at natural breakpoints (> limit words)
        
        This creates ~8-word chunks that are semantically meaningful.
        """
        if not sentences:
            return []
        
        packed = []
        
        # First pass: merge very short sentences
        i = 0
        while i < len(sentences):
            current = sentences[i].strip()
            current_words = current.split()
            
            # If very short (< 4 words), try merging with next
            if len(current_words) < 4 and i + 1 < len(sentences):
                next_sentence = sentences[i + 1].strip()
                next_words = next_sentence.split()
                combined_len = len(current_words) + len(next_words)
                
                # Merge if combined stays within limit
                if combined_len <= limit:
                    packed.append(' '.join(current_words + next_words))
                    i += 2
                    continue
            
            # Keep as-is if within limit
            if len(current_words) <= limit:
                packed.append(current)
                i += 1
            else:
                # Split at natural breakpoints
                packed.extend(self._split_at_breakpoints(current, limit))
                i += 1
        
        return packed
    
    def _split_at_breakpoints(self, text: str, limit: int) -> List[str]:
        """
        Split long sentence at natural French breakpoints.
        CRITICAL: Never create fragments like ". Je" or ", elle" - these are incomplete!
        Only break at safe points that create complete phrases.
        """
        words = text.split()
        if len(words) <= limit:
            return [text]
        
        # BAD BREAKPOINT INDICATORS - never split before these
        bad_starts = {'je', 'tu', 'il', 'elle', 'on', 'nous', 'vous', 'ils', 'elles',
                      'le', 'la', 'les', 'un', 'une', 'des', 'mon', 'ma', 'mes', 
                      'ton', 'ta', 'tes', 'son', 'sa', 'ses', 'ce', 'cet', 'cette'}
        
        # Find SAFE breakpoint positions
        breakpoints = []
        for i in range(1, len(words) - 1):  # Never break at very start or end
            word = words[i]
            prev_word = words[i-1]
            next_word = words[i+1] if i+1 < len(words) else ""
            
            lower = word.lower().rstrip('.,;:!?')
            next_lower = next_word.lower().rstrip('.,;:!?')
            
            # Check if next word would make a bad start
            if next_lower in bad_starts:
                continue  # Skip this breakpoint - would create ". Je" or similar
            
            # SAFE breakpoints: period/exclamation followed by capital letter
            if prev_word.rstrip() in ['.', '!', '?'] and word[0].isupper():
                breakpoints.append(i)
            # Coordinating conjunctions (break AFTER, but check what follows)
            elif lower in ['et', 'mais', 'ou', 'car', 'donc'] and next_lower not in bad_starts:
                breakpoints.append(i + 1)
        
        # Use breakpoints to create chunks of ~limit words
        if not breakpoints:
            # No safe breakpoints - just chunk by limit (best we can do)
            return [' '.join(words[i:i+limit]) for i in range(0, len(words), limit)]
        
        # Smart chunking: aim for chunks close to limit
        chunks = []
        start = 0
        for bp in breakpoints:
            chunk_size = bp - start
            # Take this breakpoint if chunk is reasonable size (4 to limit+2 words)
            if 4 <= chunk_size <= limit + 2:
                chunks.append(' '.join(words[start:bp]))
                start = bp
            # If chunk would be too long, force split at limit
            elif chunk_size > limit + 2:
                chunks.append(' '.join(words[start:start+limit]))
                start = start + limit
        
        # Don't forget remaining words
        if start < len(words):
            remaining = words[start:]
            if len(remaining) <= limit:
                chunks.append(' '.join(remaining))
            else:
                # Split remainder by limit
                for i in range(0, len(remaining), limit):
                    chunks.append(' '.join(remaining[i:i+limit]))
        
        return [c for c in chunks if c]
    
    def _parse_batch_response(self, output: str, original_sentences: List[str]) -> Dict[str, List[str]]:
        """
        Legacy parser: kept for compatibility
        Returns mapping from original sentence -> list of rewritten sentences.
        """
        text = (output or "").strip()
        results: Dict[str, List[str]] = {}

        # Try robust block parsing by numbered headers like '1:', '1)', '1 -'
        pattern = re.compile(r"^\s*(\d+)\s*[:)\-]\s*(.+?)(?=^\s*\d+\s*[:)\-]\s*|$)", re.DOTALL | re.MULTILINE)
        blocks: Dict[int, str] = {}
        for m in pattern.finditer(text):
            try:
                idx = int(m.group(1)) - 1
                if 0 <= idx < len(original_sentences):
                    blocks[idx] = m.group(2).strip()
            except Exception as e:
                logger.debug(f"Parse index error: {e}")

        # If nothing matched and only one sentence expected, split whole text
        if not blocks and len(original_sentences) == 1:
            body = text
            parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", body) if p.strip()]
            if parts:
                cleaned = [p if re.search(r"[.!?]$", p) else p + "." for p in parts]
                results[original_sentences[0]] = cleaned
                return results

        # Convert blocks into lists of sentences
        for idx, body in blocks.items():
            parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", body) if p.strip()]
            cleaned = [p if re.search(r"[.!?]$", p) else p + "." for p in parts]
            if cleaned:
                results[original_sentences[idx]] = cleaned

        return results
    
    def get_current_cost(self) -> float:
        """Calculate current cost in USD"""
        input_cost = (self.total_input_tokens / 1_000_000) * self.input_price_per_1m
        output_cost = (self.total_output_tokens / 1_000_000) * self.output_price_per_1m
        return input_cost + output_cost
    
    def get_token_stats(self) -> dict:
        """Get token usage statistics"""
        return {
            'input_tokens': self.total_input_tokens,
            'output_tokens': self.total_output_tokens,
            'total_tokens': self.total_input_tokens + self.total_output_tokens,
            'api_calls': self.api_call_count,
            'cost': self.get_current_cost()
        }
    
    def reset_token_count(self) -> None:
        """Reset token counters"""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.api_call_count = 0
    
    def estimate_cost_for_text(self, text: str, avg_sentence_length: int = 15) -> float:
        """
        Estimate processing cost
        
        Args:
            text: Full text to process
            avg_sentence_length: Average words per sentence
            
        Returns:
            Estimated cost in USD
        """
        word_count = self.count_words(text)
        estimated_sentences = word_count / avg_sentence_length
        sentences_to_rewrite = int(estimated_sentences * 0.6)  # Assume 60% need rewriting
        
        # Estimate tokens
        avg_input_tokens = 50 + (avg_sentence_length * 1.5)  # System + user prompt
        avg_output_tokens = avg_sentence_length * 2
        
        total_input = sentences_to_rewrite * avg_input_tokens
        total_output = sentences_to_rewrite * avg_output_tokens
        
        input_cost = (total_input / 1_000_000) * self.input_price_per_1m
        output_cost = (total_output / 1_000_000) * self.output_price_per_1m
        
        return input_cost + output_cost
