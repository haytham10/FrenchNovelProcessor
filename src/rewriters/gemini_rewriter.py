"""
Gemini AI Rewriter
Drop-in replacement for OpenAI rewriter using Google's Gemini API
Uses google-genai library with gemini-2.5-flash-lite-preview-09-2025
"""

import os
import re
import logging
from typing import List, Tuple, Optional
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class GeminiRewriter:
    """Handles AI-powered sentence rewriting using Gemini API"""
    
    def __init__(self, api_key: str, word_limit: int = 8, model: str = "gemini-2.5-flash-lite-preview-09-2025"):
        """
        Initialize the Gemini Rewriter
        
        Args:
            api_key: Google AI API key (from https://aistudio.google.com/apikey)
            word_limit: Maximum words per sentence
            model: Gemini model to use
        """
        # Initialize client with API key
        self.client = genai.Client(api_key=api_key)
        
        # Model configuration
        self.model_name = model
        self.word_limit = word_limit
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.api_call_count = 0  # Track API calls for stats
        
        # Gemini 2.5 Flash Lite pricing
        self.input_price_per_1m = 0.10
        self.output_price_per_1m = 0.40
    
    def validate_api_key(self) -> Tuple[bool, str]:
        """
        Test if API key is valid by making a minimal API call
        
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            # Simple test request
            response = self.client.models.generate_content(
                model=self.model_name,
                contents="Test"
            )
            
            # Check if we got a valid response
            if response and response.text:
                return True, "Gemini API key is valid and working!"
            else:
                return False, "Gemini API returned empty response."
                
        except Exception as e:
            error_msg = str(e)
            if "API_KEY_INVALID" in error_msg or "invalid API key" in error_msg.lower():
                return False, "Invalid Gemini API key. Get one at https://aistudio.google.com/apikey"
            elif "quota" in error_msg.lower() or "resource_exhausted" in error_msg.lower():
                return False, "API key valid but quota exceeded. Free tier: 15 RPM, 1500 RPD."
            else:
                return False, f"Gemini API error: {error_msg}"
    
    def count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough estimate)"""
        # Gemini uses similar tokenization to GPT models
        return int(len(text.split()) * 1.33)
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for AI rewriting"""
        return f"""You are a French language expert specializing in sentence restructuring.

TASK: Analyze each French sentence. If it has {self.word_limit} words or fewer, keep it as-is. If longer, rewrite it into multiple new sentences that each contain {self.word_limit} words or fewer.

CRITICAL RULES:
1. Each output sentence MUST be {self.word_limit} words or fewer (count carefully!)
2. Preserve the original meaning completely
3. Reuse as many original words as possible from the source sentence
4. Maintain proper French grammar and syntax
5. Ensure natural, fluent French
6. Output ONLY the rewritten sentences, one per line
7. NO explanations, NO commentary, NO numbering, NO bullet points
8. Keep the same tone and style as the original

ALGORITHM:
- If sentence ≤ {self.word_limit} words: output it unchanged
- If sentence > {self.word_limit} words: split into multiple sentences, each ≤ {self.word_limit} words, preserving meaning and reusing original words"""
    
    def get_full_prompt(self, sentence: str) -> str:
        """Get the complete prompt for a specific sentence"""
        word_count = self.count_words(sentence)
        return f"""{self.get_system_prompt()}

ANALYZE THIS SENTENCE:
"{sentence}"

Word count: {word_count}
Word limit: {self.word_limit}

INSTRUCTION: 
{f'This sentence is within the limit. Output it as-is.' if word_count <= self.word_limit else f'This sentence exceeds the limit. Rewrite it into multiple sentences, each with {self.word_limit} words or fewer, preserving meaning and reusing original words.'}

OUTPUT (one sentence per line, no numbering):"""
    
    @retry(
        stop=stop_after_attempt(5),  # Increased from 3 to 5 attempts
        wait=wait_exponential(multiplier=2, min=4, max=30),  # Longer waits: 4s, 8s, 16s, 30s
        retry=retry_if_exception_type((Exception,))
    )
    def rewrite_sentence(self, sentence: str) -> List[str]:
        """
        Rewrite a long sentence into shorter ones using Gemini AI
        
        Args:
            sentence: Original sentence to rewrite
            
        Returns:
            List of rewritten sentences
            
        Raises:
            Exception: If API call fails after retries
        """
        try:
            # Configure generation settings
            config = types.GenerateContentConfig(
                temperature=0.3,
                top_p=0.95,
                top_k=40,
                max_output_tokens=500
            )
            
            # Make API call
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=self.get_full_prompt(sentence),
                config=config
            )
            
            # Track API call
            self.api_call_count += 1
            
            # Track token usage from response metadata
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                if hasattr(response.usage_metadata, 'prompt_token_count'):
                    self.total_input_tokens += response.usage_metadata.prompt_token_count
                if hasattr(response.usage_metadata, 'candidates_token_count'):
                    self.total_output_tokens += response.usage_metadata.candidates_token_count
            else:
                # Fallback: estimate tokens if metadata not available
                prompt_text = self.get_full_prompt(sentence)
                self.total_input_tokens += self.estimate_tokens(prompt_text)
                self.total_output_tokens += self.estimate_tokens(response.text)
            
            # Parse response text
            content = response.text.strip()
            
            # Split into sentences (one per line)
            sentences = [s.strip() for s in content.split('\n') if s.strip()]
            
            # Clean up any numbering that might have been added
            cleaned_sentences = []
            for s in sentences:
                # Remove leading numbers, bullets, dashes
                s = re.sub(r'^[\d\.\)\-•]+\s*', '', s)
                # Remove quotation marks if they wrap the entire sentence
                s = s.strip('"\'')
                if s:
                    cleaned_sentences.append(s)
            
            return cleaned_sentences if cleaned_sentences else [sentence]
            
        except Exception as e:
            logger.error(f"Gemini rewrite error: {str(e)}")
            raise
    
    def rewrite_batch(self, sentences: list[str]) -> dict[str, list[str]]:
        """
        Rewrite multiple sentences in one API call (MUCH faster!)
        
        ALGORITHM for each sentence:
        1. If sentence has ≤ word_limit words: keep as-is
        2. If sentence has > word_limit words: rewrite into multiple sentences, each ≤ word_limit words
        
        Args:
            sentences: List of sentences to rewrite
            
        Returns:
            Dictionary mapping original sentence to list of rewritten sentences
        """
        if not sentences:
            return {}
        
        # Build batch prompt with word counts for context
        numbered_sentences = []
        for i, s in enumerate(sentences):
            wc = self.count_words(s)
            numbered_sentences.append(f"{i+1}. [{wc} words] {s}")
        
        batch_input = "\n".join(numbered_sentences)
        
        batch_prompt = f"""You are processing French sentences with a {self.word_limit}-word limit.

ALGORITHM:
- If a sentence has {self.word_limit} words or fewer: output it unchanged
- If a sentence has more than {self.word_limit} words: rewrite it into multiple sentences, each {self.word_limit} words or fewer
- Preserve meaning and reuse original words when rewriting

INPUT SENTENCES:
{batch_input}

OUTPUT FORMAT (one line per input sentence):
1: output sentence one. output sentence two.
2: output sentence.
3: output sentence one. output sentence two. output sentence three.

RULES:
- Each line MUST start with "NUMBER: "
- Each output sentence MUST be {self.word_limit} words or fewer
- If input is already ≤{self.word_limit} words, output it as-is
- If input is >{self.word_limit} words, split into multiple sentences
- Preserve original meaning and reuse original words
- NO explanations, NO extra text

OUTPUT:"""
        
        try:
            # Configure generation settings
            import time
            start_time = time.time()
            
            config = types.GenerateContentConfig(
                temperature=0.3,
                top_p=0.95,
                top_k=40,
                max_output_tokens=max(1500, len(sentences) * 100)  # Dynamic limit
            )
            
            # Make API call
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=batch_prompt,
                config=config
            )
            
            api_time = time.time() - start_time
            logger.info(f"Gemini API call for batch of {len(sentences)} took {api_time:.2f}s")
            
            # Track API call
            self.api_call_count += 1
            
            # Track token usage
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                if hasattr(response.usage_metadata, 'prompt_token_count'):
                    self.total_input_tokens += response.usage_metadata.prompt_token_count
                if hasattr(response.usage_metadata, 'candidates_token_count'):
                    self.total_output_tokens += response.usage_metadata.candidates_token_count
            else:
                # Fallback estimation
                self.total_input_tokens += self.estimate_tokens(batch_prompt)
                self.total_output_tokens += self.estimate_tokens(response.text)
            
            # Parse batch response
            content = response.text.strip()
            logger.info(f"Gemini batch response (first 500 chars): {content[:500]}")
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            results = {}
            
            # Try to parse each line
            for line in lines:
                # Skip lines that are clearly not results
                if not line or line.startswith('INPUT') or line.startswith('OUTPUT') or line.startswith('RULE'):
                    continue
                    
                # Try format: "1: sentence" or "1. sentence"
                if ':' in line or ('. ' in line and line[0].isdigit()):
                    try:
                        # Handle both "1: text" and "1. text" formats
                        if ':' in line:
                            num_str, rewrites = line.split(':', 1)
                        else:
                            # Handle "1. text" format
                            parts = line.split('. ', 1)
                            if len(parts) == 2 and parts[0].isdigit():
                                num_str, rewrites = parts
                            else:
                                continue
                        
                        idx = int(num_str.strip().rstrip('.')) - 1
                        
                        if 0 <= idx < len(sentences):
                            # Split into individual sentences
                            rewritten = [s.strip() for s in rewrites.split('.') if s.strip()]
                            # Add periods back
                            rewritten = [s if s.endswith('.') else s + '.' for s in rewritten]
                            results[sentences[idx]] = rewritten
                            logger.debug(f"Parsed sentence {idx+1}: {rewritten}")
                        else:
                            logger.warning(f"Index {idx+1} out of range (batch size: {len(sentences)})")
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Failed to parse line: '{line}' - Error: {e}")
                        continue
            
            logger.info(f"Gemini batch parsing complete: {len(results)}/{len(sentences)} sentences parsed")
            
            return results
            
        except Exception as e:
            logger.error(f"Gemini batch rewrite error: {str(e)}")
            raise
    
    def get_current_cost(self) -> float:
        """
        Calculate current cost based on tokens used
        
        Returns:
            Cost in USD
        """
        input_cost = (self.total_input_tokens / 1_000_000) * self.input_price_per_1m
        output_cost = (self.total_output_tokens / 1_000_000) * self.output_price_per_1m
        return input_cost + output_cost
    
    def estimate_cost_for_text(self, text: str, avg_sentence_length: int = 15) -> float:
        """
        Estimate cost for processing a text
        
        Args:
            text: Full text to process
            avg_sentence_length: Average words per sentence
            
        Returns:
            Estimated cost in USD
        """
        # Estimate number of sentences
        word_count = self.count_words(text)
        estimated_sentences = word_count / avg_sentence_length
        
        # Estimate sentences that need rewriting (assume 60% exceed word limit)
        sentences_to_rewrite = int(estimated_sentences * 0.6)
        
        # Estimate tokens per API call
        system_prompt = self.get_system_prompt()
        sample_prompt = self.get_full_prompt(" ".join(["word"] * avg_sentence_length))
        avg_input_tokens = self.estimate_tokens(sample_prompt)
        avg_output_tokens = avg_sentence_length * 2  # Rough estimate
        
        total_input_tokens = sentences_to_rewrite * avg_input_tokens
        total_output_tokens = sentences_to_rewrite * avg_output_tokens
        
        input_cost = (total_input_tokens / 1_000_000) * self.input_price_per_1m
        output_cost = (total_output_tokens / 1_000_000) * self.output_price_per_1m
        
        return input_cost + output_cost
    
    def reset_token_count(self):
        """Reset token counters"""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.api_call_count = 0
    
    def get_token_stats(self) -> dict:
        """Get current token usage statistics"""
        return {
            'input_tokens': self.total_input_tokens,
            'output_tokens': self.total_output_tokens,
            'total_tokens': self.total_input_tokens + self.total_output_tokens,
            'cost': self.get_current_cost(),
            'api_call_count': self.api_call_count
        }
