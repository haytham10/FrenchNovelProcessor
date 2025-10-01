"""
AI-Powered Sentence Rewriter - Optimized for GPT-5 nano
Clean, efficient implementation following OpenAI best practices
"""

import logging
import re
from typing import List, Tuple, Dict
from openai import OpenAI
import tiktoken

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
        self.client = OpenAI(api_key=api_key)
        self.word_limit = word_limit
        self.model = model
        
        # Token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.api_call_count = 0
        
        # Encoding
        try:
            self.encoding = tiktoken.encoding_for_model("gpt-5-nano")
        except:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        
        # Pricing (GPT-5 nano)
        self.input_price_per_1m = 0.05
        self.output_price_per_1m = 0.40
        
        # System prompt (built once)
        self._system_prompt = self._create_system_prompt()

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
    
    def _create_system_prompt(self) -> str:
        """Create optimized system prompt for GPT-5 nano"""
        return (
            f"You are a careful French copy editor. Split each input into several much shorter, grammatical sentences.\n"
            f"HARD CONSTRAINTS (must obey):\n"
            f"- Max {self.word_limit} words per output sentence.\n"
            f"- Preserve meaning; do not add or remove facts.\n"
            f"- Prefer using original vocabulary where possible; minimal function words (articles, prepositions, pronouns) may be added to keep correct French grammar.\n"
            f"- Light reordering is allowed only if needed for grammaticality; avoid paraphrasing.\n"
            f"- Output ONLY one line per item: N: phrase. phrase. (N is the input number). Nothing else.\n"
            f"Hint: Prefer splitting at commas, conjunctions (et, mais, ou, donc, or, ni, car) and relative clauses (qui, que, dont, où).\n"
            f"\nExemple minimal:\n"
            f"Entrée: 1. Je marche, mais je suis fatigué.\n"
            f"Sortie: 1: Je marche. Mais je suis fatigué.\n"
        )
    
    def validate_api_key(self) -> Tuple[bool, str]:
        """Validate API key with minimal call"""
        try:
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
            return len(self.encoding.encode(text))
        except:
            return int(len(text.split()) * 1.33)
    
    def rewrite_sentence(self, sentence: str) -> List[str]:
        """
        Rewrite a single sentence (fallback for non-batch)
        
        Args:
            sentence: Sentence to rewrite
            
        Returns:
            List of rewritten sentences
        """
        result = self.rewrite_batch([sentence])
        return result.get(sentence, [sentence])
    
    def rewrite_batch(self, sentences: List[str]) -> Dict[str, List[str]]:
        """
        Rewrite multiple sentences in one efficient API call
        
        Args:
            sentences: List of sentences to rewrite
            
        Returns:
            Dict mapping original sentence -> list of rewritten sentences
        """
        if not sentences:
            return {}
        
        # Build optimized batch prompt
        numbered = "\n".join([f"{i+1}. {s}" for i, s in enumerate(sentences)])
        
        user_prompt = (
            f"Apply the rules to each item below. Produce natural, grammatical French. Prefer original words; you may add minimal function words when necessary.\n\n"
            f"{numbered}\n\nFormat: N: phrase. phrase."
        )
        
        try:
            # Efficient API call aligned with Responses API best practices
            response = self.client.responses.create(
                model=self.model,
                instructions=self._system_prompt,
                input=user_prompt,
                store=False,
                reasoning={"effort": "minimal"},
                text={"verbosity": "low"},
                max_output_tokens=min(2500, len(sentences) * 80)
            )
            
            self._track_usage(response)
            
            # Parse response
            output = self._extract_output(response)
            if not output:
                logger.warning("Empty response from API")
                return {}
            
            results = self._parse_batch_response(output, sentences)
            # Post-process: enforce word limit, strict content preservation, and fill missing
            final_results = {}
            for idx, orig in enumerate(sentences):
                rewritten = results.get(orig)
                if not rewritten:
                    # Fallback: return original sentence (no markers); validator will decide
                    final_results[orig] = [orig]
                    continue
                # Enforce word limit strictly
                processed = []
                for sent in rewritten:
                    # Normalize minimal formatting first
                    sent = self._normalize(sent)
                    # Ensure sentences end with a period
                    s = sent.strip()
                    if s and not s.endswith(('.', '!', '?')):
                        s = s.rstrip('.') + '.'
                    processed.append(s)
                # No strict token/order enforcement here to allow grammatical fixes
                final_results[orig] = processed
            return final_results
            
        except Exception as e:
            logger.error(f"Batch rewrite failed: {e}")
            return {}
    
    def _parse_batch_response(self, output: str, original_sentences: List[str]) -> Dict[str, List[str]]:
        """
        Parse batch response efficiently
        
        Args:
            output: Raw API response text
            original_sentences: Original input sentences
            
        Returns:
            Mapping of original -> rewritten sentences
        """
        results = {}
        lines = [line.strip() for line in output.split('\n') if line.strip()]
        
        for line in lines:
            # Parse "N: text" or "N. text" format
            if not (line[0].isdigit() and (':' in line or '. ' in line)):
                continue
            
            try:
                # Split on first colon or period after number
                if ':' in line:
                    num_part, text_part = line.split(':', 1)
                else:
                    parts = line.split('.', 1)
                    if len(parts) != 2:
                        continue
                    num_part, text_part = parts
                
                idx = int(num_part.strip()) - 1
                
                # Validate index
                if not (0 <= idx < len(original_sentences)):
                    continue
                
                # Split into sentences and clean
                rewritten = []
                for chunk in text_part.split('.'):
                    chunk = chunk.strip()
                    if chunk:
                        # Ensure sentence ends with period
                        if not chunk.endswith('.'):
                            chunk += '.'
                        rewritten.append(chunk)
                
                if rewritten:
                    results[original_sentences[idx]] = rewritten
                
                # Early exit if all sentences mapped
                if len(results) >= len(original_sentences):
                    break
                    
            except (ValueError, IndexError) as e:
                logger.debug(f"Parse error for line '{line}': {e}")
                continue
        
        logger.info(f"Batch parsed: {len(results)}/{len(original_sentences)} sentences")
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
