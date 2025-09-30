"""
Sentence Validation Module
Validates AI-rewritten sentences for quality and correctness
"""

import re
from typing import List, Tuple, Set
from langdetect import detect, LangDetectException


class SentenceValidator:
    """Validates rewritten sentences meet quality criteria"""
    
    def __init__(self, word_limit: int = 8):
        """
        Initialize validator
        
        Args:
            word_limit: Maximum words per sentence
        """
        self.word_limit = word_limit
    
    def count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    def is_french(self, text: str) -> bool:
        """
        Check if text is in French
        
        Args:
            text: Text to check
            
        Returns:
            True if French, False otherwise
        """
        try:
            # Skip very short texts
            if len(text.split()) < 2:
                return True  # Assume short texts are OK
            
            lang = detect(text)
            return lang == 'fr'
        except LangDetectException:
            # If detection fails, assume it's OK
            return True
    
    def extract_key_words(self, text: str) -> Set[str]:
        """
        Extract key words (nouns, verbs) from text
        Simple approach: words longer than 3 characters, lowercase
        
        Args:
            text: Text to extract from
            
        Returns:
            Set of key words
        """
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text.lower())
        
        # Common French stopwords to exclude
        stopwords = {
            'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'et', 'ou',
            'mais', 'donc', 'car', 'qui', 'que', 'quoi', 'dont', 'où',
            'dans', 'sur', 'sous', 'avec', 'sans', 'pour', 'par', 'vers',
            'chez', 'être', 'avoir', 'son', 'sa', 'ses', 'mon', 'ma', 'mes',
            'ton', 'ta', 'tes', 'leur', 'leurs', 'notre', 'nos', 'votre', 'vos',
            'ce', 'cet', 'cette', 'ces', 'il', 'elle', 'ils', 'elles',
            'je', 'tu', 'nous', 'vous', 'me', 'te', 'se', 'lui', 'en', 'y',
            'ne', 'pas', 'plus', 'très', 'tout', 'tous', 'toute', 'toutes',
            'bien', 'encore', 'déjà', 'aussi', 'ainsi', 'donc', 'alors'
        }
        
        words = text.split()
        key_words = {w for w in words if len(w) > 3 and w not in stopwords}
        
        return key_words
    
    def check_content_preservation(self, original: str, rewritten_list: List[str]) -> float:
        """
        Check if key content is preserved in rewritten sentences
        
        Args:
            original: Original sentence
            rewritten_list: List of rewritten sentences
            
        Returns:
            Similarity score (0-1), higher is better
        """
        original_keys = self.extract_key_words(original)
        
        if not original_keys:
            return 1.0  # No key words to preserve
        
        # Combine all rewritten sentences
        combined_rewritten = ' '.join(rewritten_list)
        rewritten_keys = self.extract_key_words(combined_rewritten)
        
        # Calculate overlap
        overlap = len(original_keys & rewritten_keys)
        total = len(original_keys)
        
        return overlap / total if total > 0 else 1.0
    
    def validate_word_count(self, sentences: List[str]) -> Tuple[bool, List[int]]:
        """
        Check if all sentences meet word count requirement
        
        Args:
            sentences: List of sentences to check
            
        Returns:
            Tuple of (all_valid, list_of_word_counts)
        """
        word_counts = [self.count_words(s) for s in sentences]
        all_valid = all(count <= self.word_limit for count in word_counts)
        return all_valid, word_counts
    
    def validate_language(self, sentences: List[str]) -> Tuple[bool, List[bool]]:
        """
        Check if all sentences are in French
        
        Args:
            sentences: List of sentences to check
            
        Returns:
            Tuple of (all_french, list_of_language_checks)
        """
        language_checks = [self.is_french(s) for s in sentences]
        all_french = all(language_checks)
        return all_french, language_checks
    
    def validate_rewrite(self, original: str, rewritten_list: List[str]) -> Tuple[bool, str, dict]:
        """
        Comprehensive validation of rewritten sentences
        
        Args:
            original: Original sentence
            rewritten_list: List of rewritten sentences
            
        Returns:
            Tuple of (is_valid, error_message, details_dict)
        """
        details = {}
        
        # Check if we have any output
        if not rewritten_list or len(rewritten_list) == 0:
            return False, "No rewritten sentences generated", details
        
        # Check word count
        word_count_valid, word_counts = self.validate_word_count(rewritten_list)
        details['word_counts'] = word_counts
        
        if not word_count_valid:
            invalid_sentences = [
                f"Sentence {i+1} has {wc} words (limit: {self.word_limit})"
                for i, wc in enumerate(word_counts) if wc > self.word_limit
            ]
            return False, "Word count exceeded: " + "; ".join(invalid_sentences), details
        
        # Check language
        language_valid, language_checks = self.validate_language(rewritten_list)
        details['language_checks'] = language_checks
        
        if not language_valid:
            non_french = [
                f"Sentence {i+1} may not be French"
                for i, is_fr in enumerate(language_checks) if not is_fr
            ]
            return False, "Language validation failed: " + "; ".join(non_french), details
        
        # Check content preservation
        similarity = self.check_content_preservation(original, rewritten_list)
        details['similarity_score'] = similarity
        
        if similarity < 0.4:  # Less than 40% key words preserved
            return False, f"Content preservation low (similarity: {similarity:.2%})", details
        
        # All checks passed
        return True, "All validation checks passed", details
    
    def validate_simple(self, sentences: List[str]) -> bool:
        """
        Simple validation: just check word count
        Faster for quick checks
        
        Args:
            sentences: List of sentences to check
            
        Returns:
            True if all valid, False otherwise
        """
        return all(self.count_words(s) <= self.word_limit for s in sentences)
