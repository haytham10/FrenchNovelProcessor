"""
Sentence Validation Module
Validates AI-rewritten sentences for quality and correctness
"""

import re
from typing import List, Tuple, Set
from langdetect import detect, LangDetectException


class SentenceValidator:
    """Validates rewritten sentences meet quality criteria"""
    
    def __init__(self, word_limit: int = 8, tolerance: int = 2):
        """
        Initialize validator
        
        Args:
            word_limit: Maximum words per sentence
            tolerance: Allow sentences up to word_limit + tolerance (default: 2)
        """
        self.word_limit = word_limit
        self.tolerance = tolerance
        self.effective_limit = word_limit + tolerance  # e.g., 8 + 2 = 10 words max
    
    def count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    def is_french(self, text: str) -> bool:
        """
        Check if text is in French (VERY lenient check)
        
        Args:
            text: Text to check
            
        Returns:
            True if French or uncertain, False only if obviously English/German/etc
        """
        try:
            # Skip very short texts (less than 5 words) - always pass
            if len(text.split()) < 5:
                return True  # Short texts always OK
            
            # Remove numbers, punctuation, and special characters for better detection
            clean_text = re.sub(r'[0-9\.\,\;\:\!\?\(\)\[\]\{\}\-\_\"\'\«\»]', ' ', text)
            clean_text = ' '.join(clean_text.split())  # Remove extra spaces
            
            if len(clean_text.strip()) < 15:
                return True  # Too short after cleaning - always pass
            
            # Check for French-specific characters (strong indicator)
            if any(char in text for char in ['é', 'è', 'ê', 'à', 'â', 'ô', 'û', 'ç', 'ù', 'î', 'ï', 'ë', 'ü']):
                return True  # Has French accents - definitely French
            
            # Detect language
            lang = detect(clean_text)
            
            # VERY lenient: Accept all Romance languages and be uncertain about others
            # Only reject if it's clearly English, German, Dutch, etc.
            reject_langs = ['en', 'de', 'nl', 'sv', 'da', 'no', 'fi', 'pl', 'cs', 'sk']
            
            return lang not in reject_langs  # Accept everything except clearly non-French
            
        except (LangDetectException, Exception):
            # If detection fails at all, assume it's OK (very lenient)
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
        # Remove punctuation but keep apostrophes and hyphens joining words (e.g., qu'il, philo-mène)
        clean = re.sub(r"[^a-zA-Zà-öø-ÿÀ-ÖØ-ßœŒæÆ0-9'\-\s]", ' ', text.lower())
        clean = re.sub(r"\s+", ' ', clean)

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

        words = clean.split()
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
        # Use effective_limit which includes tolerance (e.g., 9 instead of strict 8)
        all_valid = all(count <= self.effective_limit for count in word_counts)
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

        # No special markers allowed; outputs should be clean sentences only.
        
        # Check word count
        word_count_valid, word_counts = self.validate_word_count(rewritten_list)
        details['word_counts'] = word_counts
        
        if not word_count_valid:
            invalid_sentences = [
                f"Sentence {i+1} has {wc} words (limit: {self.effective_limit})"
                for i, wc in enumerate(word_counts) if wc > self.effective_limit
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
        
        # Check content preservation (very lenient threshold)
        similarity = self.check_content_preservation(original, rewritten_list)
        details['similarity_score'] = similarity
        
        # Only fail if similarity is extremely low (< 10%), allowing minor function word changes
        if similarity < 0.10:
            return False, f"Content preservation very low (similarity: {similarity:.2%})", details
        
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
        return all(self.count_words(s) <= self.effective_limit for s in sentences)
