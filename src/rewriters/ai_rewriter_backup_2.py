"""
French Text Processor - V2 Complete Rewrite
============================================
Revolutionary approach: Let AI do what it's best at, keep post-processing minimal.

Core Strategy:
1. Give AI ONE clear, unambiguous task with examples
2. Simple, fast parsing (no complex logic)
3. Minimal validation - trust AI, fix only real errors
4. Focus on SPEED and RELIABILITY over complex algorithms
"""

import logging
import re
from typing import List, Dict, Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

logger = logging.getLogger(__name__)


class FrenchTextProcessor:

    def __init__(self, api_key: str, word_limit: int = 8, model: str = "gpt-4o-mini"):
        """
        Initialize processor
        
        Args:
            api_key: OpenAI API key
            word_limit: Target words per chunk (default: 8)
            model: OpenAI model (default: gpt-4o-mini for speed/cost)
        """
        if OpenAI is None:
            raise ImportError("OpenAI package required: pip install openai")
        
        self.client = OpenAI(api_key=api_key)
        self.word_limit = word_limit
        self.model = model
        
        # Stats
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.api_call_count = 0

    def process(self, text_segments: List[str]) -> Dict[str, List[str]]:
        """
        Process text segments into 8-word chunks
        
        Args:
            text_segments: List of text segments to process
            
        Returns:
            Dict mapping original segment -> list of processed chunks
        """
        if not text_segments:
            return {}
        
        # AI processing
        ai_results = self._call_ai(text_segments)
        
        # Minimal cleanup
        final_results = {}
        for orig in text_segments:
            chunks = ai_results.get(orig, [orig])
            final_results[orig] = self._cleanup_chunks(chunks)
        
        return final_results

    def _call_ai(self, segments: List[str]) -> Dict[str, List[str]]:
        """
        Single AI call with crystal-clear instructions and examples
        """
        # Build numbered input
        numbered = "\n".join([f"{i+1}. {s}" for i, s in enumerate(segments)])
        
        # THE PERFECT PROMPT: Clear, with examples, unambiguous format
        prompt = f"""Split French text into sentences of EXACTLY {self.word_limit} words or less.

CRITICAL RULES:
• Each sentence: {self.word_limit} words maximum (count carefully!)
• Each sentence must be a complete, meaningful phrase
• Use ALL words from original in exact order
• Fix OCR errors: "gâ teaux"→"gâteaux", "de­ vant"→"devant"
• Never end with ", elle" or ". Je" - these are incomplete
• Output format: "1) sentence" (one per line)

EXAMPLES:
Input: "Moma, ma mère, reste debout devant moi avec la robe."
Output:
1) Moma, ma mère, reste debout devant
1) moi avec la robe

Input: "Je n'aime pas être déguisée. Je préfère regarder les gens."
Output:
2) Je n'aime pas être déguisée
2) Je préfère regarder les gens

NOW PROCESS:
{numbered}"""

        # Call AI
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You split French text into {self.word_limit}-word chunks. Count words carefully. Never exceed {self.word_limit} words."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temp for more consistent output
                max_tokens=len(segments) * 100
            )
            
            self._track_usage(response)
            output = response.choices[0].message.content
            
            return self._parse_output(output, segments)
            
        except Exception as e:
            logger.error(f"AI call failed: {e}")
            # Fallback: return originals
            return {s: [s] for s in segments}

    def _parse_output(self, output: str, originals: List[str]) -> Dict[str, List[str]]:
        """
        Parse AI output - SIMPLE and ROBUST
        Format: "1) chunk text"
        """
        results = {}
        
        for line in output.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Match "1) text" or "1. text" or "1: text"
            match = re.match(r'^(\d+)[).:\-]\s*(.+)$', line)
            if not match:
                continue
            
            try:
                idx = int(match.group(1)) - 1
                chunk = match.group(2).strip()
            except (ValueError, IndexError):
                continue
            
            if idx < 0 or idx >= len(originals):
                continue
            
            orig = originals[idx]
            
            # Clean chunk
            chunk = self._clean_chunk(chunk)
            if not chunk:
                continue
            
            if orig not in results:
                results[orig] = []
            results[orig].append(chunk)
        
        # Ensure every original has a result
        for orig in originals:
            if orig not in results:
                results[orig] = [orig]
        
        return results

    def _clean_chunk(self, chunk: str) -> str:
        """
        Minimal cleanup: remove trailing punctuation, fix spacing
        """
        # Remove trailing periods (output format doesn't need them)
        chunk = chunk.rstrip('.!?,;:—–-')
        
        # Fix common OCR spacing issues
        chunk = re.sub(r'\s+', ' ', chunk)  # Multiple spaces → single space
        chunk = re.sub(r'(\w)\s+-\s+(\w)', r'\1-\2', chunk)  # "de - puis" → "depuis"
        
        # Remove page numbers at end (trailing digits)
        chunk = re.sub(r'\s+\d{1,3}$', '', chunk)
        
        return chunk.strip()

    def _cleanup_chunks(self, chunks: List[str]) -> List[str]:
        """
        Post-process chunks: enforce word limit, merge tiny fragments
        """
        cleaned = []
        buffer = []
        buffer_words = 0
        
        for chunk in chunks:
            words = chunk.split()
            word_count = len(words)
            
            # If chunk exceeds limit, split it
            if word_count > self.word_limit:
                # Flush buffer first
                if buffer:
                    cleaned.append(' '.join(buffer))
                    buffer = []
                    buffer_words = 0
                
                # Split long chunk
                for i in range(0, len(words), self.word_limit):
                    cleaned.append(' '.join(words[i:i + self.word_limit]))
                continue
            
            # Try to merge small chunks (< 3 words) with next
            if buffer_words + word_count <= self.word_limit:
                buffer.extend(words)
                buffer_words += word_count
            else:
                # Flush buffer
                if buffer:
                    cleaned.append(' '.join(buffer))
                buffer = words
                buffer_words = word_count
        
        # Don't forget remaining buffer
        if buffer:
            cleaned.append(' '.join(buffer))
        
        return [c for c in cleaned if c]

    def _track_usage(self, response) -> None:
        """Track API usage"""
        self.api_call_count += 1
        if hasattr(response, 'usage'):
            self.total_input_tokens += response.usage.prompt_tokens
            self.total_output_tokens += response.usage.completion_tokens

    def get_stats(self) -> dict:
        """Get usage statistics"""
        return {
            'api_calls': self.api_call_count,
            'input_tokens': self.total_input_tokens,
            'output_tokens': self.total_output_tokens,
            'total_tokens': self.total_input_tokens + self.total_output_tokens
        }

    # Legacy compatibility
    def rewrite_sentence(self, sentence: str) -> List[str]:
        """Process single sentence (legacy API)"""
        result = self.process([sentence])
        return result.get(sentence, [sentence])
    
    def rewrite_batch(self, sentences: List[str]) -> Dict[str, List[str]]:
        """Process batch (legacy API)"""
        return self.process(sentences)

AIRewriter = FrenchTextProcessor
