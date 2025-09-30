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
        return f"""You are a French language expert specializing in sentence simplification.
Your task is to rewrite long French sentences into shorter, grammatically correct sentences while preserving the original meaning and using as many original words as possible.

Rules:
1. Each new sentence must be {self.word_limit} words or fewer
2. Maintain proper French grammar and syntax
3. Preserve the original meaning completely
4. Reuse original words whenever possible
5. Ensure natural, fluent French
6. Output only the rewritten sentences, one per line
7. Do not add explanations or commentary
8. Do not add numbering or bullet points
9. Keep the same tone and style as the original"""
    
    def get_full_prompt(self, sentence: str) -> str:
        """Get the complete prompt for a specific sentence"""
        return f"""{self.get_system_prompt()}

Rewrite this French sentence into multiple shorter sentences, each containing {self.word_limit} words or fewer:

"{sentence}"

Output format: One sentence per line, no numbering."""
    
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
    
    def get_token_stats(self) -> dict:
        """Get current token usage statistics"""
        return {
            'input_tokens': self.total_input_tokens,
            'output_tokens': self.total_output_tokens,
            'total_tokens': self.total_input_tokens + self.total_output_tokens,
            'cost': self.get_current_cost()
        }
