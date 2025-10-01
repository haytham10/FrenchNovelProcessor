"""
Test Optimization Features
Validates that optimization features work correctly
"""

import unittest
from src.core.sentence_splitter import SentenceSplitter, ProcessingMode
from src.utils.sentence_cache import SentenceCache
from src.utils.performance_metrics import PerformanceMetrics


class TestSentenceCache(unittest.TestCase):
    """Test sentence caching functionality"""
    
    def setUp(self):
        """Set up test cache"""
        self.cache = SentenceCache(max_size=10)
    
    def test_cache_put_and_get(self):
        """Test basic cache operations"""
        sentence = "Le chat noir dort."
        rewritten = ["Le chat dort.", "Le chat est noir."]
        
        # Put in cache
        self.cache.put(sentence, rewritten)
        
        # Get from cache
        result = self.cache.get(sentence)
        self.assertEqual(result, rewritten)
    
    def test_cache_miss(self):
        """Test cache miss"""
        result = self.cache.get("Sentence not in cache")
        self.assertIsNone(result)
    
    def test_cache_normalization(self):
        """Test that cache normalizes sentences"""
        sentence1 = "Le chat dort."
        sentence2 = "LE CHAT DORT."  # Different case
        rewritten = ["Le chat dort."]
        
        self.cache.put(sentence1, rewritten)
        result = self.cache.get(sentence2)
        self.assertIsNotNone(result)  # Should find it despite case difference
    
    def test_cache_eviction(self):
        """Test LRU eviction"""
        # Fill cache to max
        for i in range(10):
            self.cache.put(f"Sentence {i}", [f"Rewritten {i}"])
        
        # Add one more - should evict oldest
        self.cache.put("Sentence 10", ["Rewritten 10"])
        
        # First sentence should be evicted
        result = self.cache.get("Sentence 0")
        self.assertIsNone(result)
        
        # Last sentence should be present
        result = self.cache.get("Sentence 10")
        self.assertIsNotNone(result)
    
    def test_cache_stats(self):
        """Test cache statistics"""
        # Add some entries
        self.cache.put("Test 1", ["Result 1"])
        self.cache.put("Test 2", ["Result 2"])
        
        # Hit and miss
        self.cache.get("Test 1")  # Hit
        self.cache.get("Test 3")  # Miss
        
        stats = self.cache.get_stats()
        self.assertEqual(stats['hits'], 1)
        self.assertEqual(stats['misses'], 1)
        self.assertEqual(stats['size'], 2)
        self.assertGreater(stats['hit_rate'], 0)


class TestPerformanceMetrics(unittest.TestCase):
    """Test performance metrics tracking"""
    
    def test_metrics_initialization(self):
        """Test metrics object initialization"""
        metrics = PerformanceMetrics()
        
        self.assertEqual(metrics.total_sentences, 0)
        self.assertEqual(metrics.api_calls, 0)
        self.assertEqual(metrics.cache_hits, 0)
    
    def test_batch_recording(self):
        """Test batch statistics recording"""
        metrics = PerformanceMetrics()
        
        metrics.record_batch(25, 1.5)
        metrics.record_batch(30, 2.0)
        
        self.assertEqual(len(metrics.batch_sizes), 2)
        self.assertEqual(metrics.get_avg_batch_size(), 27.5)
        self.assertEqual(metrics.get_avg_batch_time(), 1.75)
    
    def test_timing(self):
        """Test timing functionality"""
        import time
        
        metrics = PerformanceMetrics()
        metrics.start_timer()
        time.sleep(0.1)  # Sleep for 100ms
        metrics.end_timer()
        
        total_time = metrics.get_total_time()
        self.assertGreater(total_time, 0.09)  # At least 90ms
        self.assertLess(total_time, 0.2)      # Less than 200ms
    
    def test_summary_generation(self):
        """Test summary generation"""
        metrics = PerformanceMetrics()
        metrics.start_timer()
        
        # Simulate some processing
        metrics.total_sentences = 100
        metrics.direct_sentences = 40
        metrics.ai_rewrites = 50
        metrics.mechanical_fallbacks = 10
        metrics.api_calls = 10
        metrics.cache_hits = 15
        
        metrics.end_timer()
        
        summary = metrics.get_summary()
        
        # Check all sections exist
        self.assertIn('speed', summary)
        self.assertIn('efficiency', summary)
        self.assertIn('quality', summary)
        self.assertIn('cost', summary)
        
        # Check specific values
        self.assertEqual(summary['quality']['total_sentences'], 100)


class TestAdaptiveBatching(unittest.TestCase):
    """Test adaptive batching functionality"""
    
    def test_optimal_batch_size_simple(self):
        """Test batch size for simple sentences"""
        # Create splitter in mechanical mode (no API key needed)
        splitter = SentenceSplitter(word_limit=8, mode=ProcessingMode.MECHANICAL_CHUNKING)
        
        # Test with simple sentences (avg 10 words)
        batch_size = splitter._get_optimal_batch_size(10)
        self.assertEqual(batch_size, 35)
    
    def test_optimal_batch_size_medium(self):
        """Test batch size for medium sentences"""
        splitter = SentenceSplitter(word_limit=8, mode=ProcessingMode.MECHANICAL_CHUNKING)
        
        # Test with medium sentences (avg 15 words)
        batch_size = splitter._get_optimal_batch_size(15)
        self.assertEqual(batch_size, 25)
    
    def test_optimal_batch_size_complex(self):
        """Test batch size for complex sentences"""
        splitter = SentenceSplitter(word_limit=8, mode=ProcessingMode.MECHANICAL_CHUNKING)
        
        # Test with complex sentences (avg 22 words)
        batch_size = splitter._get_optimal_batch_size(22)
        self.assertEqual(batch_size, 15)


class TestPrefiltering(unittest.TestCase):
    """Test pre-filtering logic"""
    
    def test_direct_passthrough(self):
        """Test that short sentences pass through directly"""
        splitter = SentenceSplitter(word_limit=8, mode=ProcessingMode.MECHANICAL_CHUNKING)
        
        short_sentence = "Le chat dort."  # 3 words
        result = splitter.process_sentence(short_sentence)
        
        self.assertEqual(result.method, "Direct")
        self.assertEqual(result.output_sentences, [short_sentence])
    
    def test_mechanical_for_long(self):
        """Test that very long sentences use mechanical chunking"""
        splitter = SentenceSplitter(word_limit=8, mode=ProcessingMode.MECHANICAL_CHUNKING)
        
        # Create a sentence with 35 words
        long_sentence = " ".join(["mot"] * 35) + "."
        result = splitter.process_sentence(long_sentence)
        
        # Should be chunked
        self.assertIn("Mechanical", result.method)
        self.assertGreater(len(result.output_sentences), 1)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
