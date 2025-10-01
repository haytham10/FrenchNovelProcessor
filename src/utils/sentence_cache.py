"""
Sentence Cache Module
Simple LRU cache for AI-rewritten sentences to improve performance
"""

import re
import logging
from typing import List, Optional, Dict
from collections import OrderedDict

logger = logging.getLogger(__name__)


class SentenceCache:
    """
    Simple LRU cache for sentence rewrites
    
    Caches AI-rewritten sentences to avoid redundant API calls
    for identical or similar sentences (e.g., repeated dialogue, common phrases)
    """
    
    def __init__(self, max_size: int = 500):
        """
        Initialize cache
        
        Args:
            max_size: Maximum number of sentences to cache
        """
        self.max_size = max_size
        self.cache: OrderedDict[str, List[str]] = OrderedDict()
        self.hits: int = 0
        self.misses: int = 0
    
    def _normalize(self, sentence: str) -> str:
        """
        Normalize sentence for consistent cache lookup
        
        Args:
            sentence: Original sentence
            
        Returns:
            Normalized sentence
        """
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', sentence.strip())
        
        # Convert to lowercase for case-insensitive matching
        normalized = normalized.lower()
        
        # Remove some punctuation variations for better matching
        normalized = normalized.replace('"', '"').replace('"', '"')
        normalized = normalized.replace("'", "'").replace("'", "'")
        
        return normalized
    
    def get(self, sentence: str) -> Optional[List[str]]:
        """
        Get cached rewrite for sentence
        
        Args:
            sentence: Sentence to look up
            
        Returns:
            Cached rewritten sentences or None if not found
        """
        normalized = self._normalize(sentence)
        
        if normalized in self.cache:
            self.hits += 1
            # Move to end (most recently used)
            self.cache.move_to_end(normalized)
            return self.cache[normalized]
        
        self.misses += 1
        return None
    
    def put(self, sentence: str, rewritten: List[str]):
        """
        Cache a sentence rewrite
        
        Args:
            sentence: Original sentence
            rewritten: List of rewritten sentences
        """
        normalized = self._normalize(sentence)
        
        # Remove oldest entry if cache is full
        if len(self.cache) >= self.max_size:
            # Remove least recently used (first item)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            logger.debug(f"Cache full, evicted oldest entry")
        
        self.cache[normalized] = rewritten
    
    def clear(self):
        """Clear the cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> Dict[str, any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0.0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'total_requests': total_requests,
            'hit_rate': hit_rate,
            'utilization': (len(self.cache) / self.max_size * 100) if self.max_size > 0 else 0.0
        }
    
    def __len__(self) -> int:
        """Get current cache size"""
        return len(self.cache)
    
    def __contains__(self, sentence: str) -> bool:
        """Check if sentence is in cache"""
        normalized = self._normalize(sentence)
        return normalized in self.cache
