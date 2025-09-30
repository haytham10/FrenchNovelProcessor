"""
AI-Powered Sentence Rewriter
Uses OpenAI GPT-4o-mini to intelligently rewrite long French sentences
"""

import os
import re
import logging
from typing import List, Tuple, Optional
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import tiktoken

logger = logging.getLogger(__name__)


class AIRewriter:
    """Handles AI-powered sentence rewriting using OpenAI API"""
    
    def __init__(self, api_key: str, word_limit: int = 8, model: str = "gpt-4o-mini"):
        """
        Initialize the AI Rewriter
        
        Args:
            api_key: OpenAI API key
            word_limit: Maximum words per sentence
            model: OpenAI model to use (default: gpt-4o-mini)
        """
        self.client = OpenAI(api_key=api_key)
        self.word_limit = word_limit
        self.model = model
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        # Use cl100k_base encoding for GPT-4o models
        try:
            self.encoding = tiktoken.encoding_for_model("gpt-4o")
        except:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        
        # Pricing per 1M tokens (as of 2025)
        self.input_price_per_1m = 0.150
        self.output_price_per_1m = 0.600
    
    def validate_api_key(self) -> Tuple[bool, str]:
        """
        Test if API key is valid by making a minimal API call
        
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Test"}
                ],
                max_tokens=5
            )
            return True, "API key is valid and working!"
        except Exception as e:
            error_msg = str(e)
            if "invalid_api_key" in error_msg or "Incorrect API key" in error_msg:
                return False, "Invalid API key. Please check your key and try again."
            elif "insufficient_quota" in error_msg:
                return False, "API key is valid but you have insufficient credits. Please add credits to your OpenAI account."
            else:
                return False, f"API connection error: {error_msg}"
    
    def count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        try:
            return len(self.encoding.encode(text))
        except:
            # Fallback: rough estimate (1 token ≈ 0.75 words for French)
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
    
    def get_user_prompt(self, sentence: str) -> str:
        """Get the user prompt for a specific sentence"""
        return f"""Rewrite this French sentence into multiple shorter sentences, each containing {self.word_limit} words or fewer:

"{sentence}"

Output format: One sentence per line, no numbering."""
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,))
    )
    def rewrite_sentence(self, sentence: str) -> List[str]:
        """
        Rewrite a long sentence into shorter ones using AI
        
        Args:
            sentence: Original sentence to rewrite
            
        Returns:
            List of rewritten sentences
            
        Raises:
            Exception: If API call fails after retries
        """
        try:
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.get_system_prompt()},
                    {"role": "user", "content": self.get_user_prompt(sentence)}
                ],
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=500
            )
            
            # Track token usage
            self.total_input_tokens += response.usage.prompt_tokens
            self.total_output_tokens += response.usage.completion_tokens
            
            # Parse response
            content = response.choices[0].message.content.strip()
            
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
            logger.error(f"AI rewrite error: {str(e)}")
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
        system_prompt_tokens = self.estimate_tokens(self.get_system_prompt())
        avg_user_prompt_tokens = self.estimate_tokens(f"Rewrite this French sentence into multiple shorter sentences, each containing {self.word_limit} words or fewer:\n\n\"" + " ".join(["word"] * avg_sentence_length) + "\"\n\nOutput format: One sentence per line, no numbering.")
        avg_response_tokens = avg_sentence_length * 2  # Rough estimate
        
        total_input_tokens = sentences_to_rewrite * (system_prompt_tokens + avg_user_prompt_tokens)
        total_output_tokens = sentences_to_rewrite * avg_response_tokens
        
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
