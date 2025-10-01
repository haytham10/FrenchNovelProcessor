"""
Performance Metrics Module
Tracks and reports processing performance and optimization effectiveness
"""

import time
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Track detailed performance metrics for optimization analysis"""
    
    def __init__(self):
        """Initialize performance tracking"""
        # Timing metrics
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.extraction_time: float = 0.0
        self.processing_time: float = 0.0
        self.validation_time: float = 0.0
        
        # Processing metrics
        self.total_sentences: int = 0
        self.direct_sentences: int = 0
        self.ai_rewrites: int = 0
        self.mechanical_fallbacks: int = 0
        self.validation_failures: int = 0
        
        # Efficiency metrics
        self.api_calls: int = 0
        self.cache_hits: int = 0
        self.tokens_used: int = 0
        
        # Batch statistics
        self.batch_sizes: list = []
        self.batch_times: list = []
        
        # Cost metrics
        self.estimated_cost: float = 0.0
        self.actual_cost: float = 0.0
    
    def start_timer(self):
        """Start overall timing"""
        self.start_time = time.time()
    
    def end_timer(self):
        """End overall timing"""
        self.end_time = time.time()
    
    def get_total_time(self) -> float:
        """Get total processing time in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    def record_batch(self, batch_size: int, batch_time: float):
        """Record batch processing statistics"""
        self.batch_sizes.append(batch_size)
        self.batch_times.append(batch_time)
    
    def get_avg_batch_size(self) -> float:
        """Get average batch size"""
        if not self.batch_sizes:
            return 0.0
        return sum(self.batch_sizes) / len(self.batch_sizes)
    
    def get_avg_batch_time(self) -> float:
        """Get average batch processing time"""
        if not self.batch_times:
            return 0.0
        return sum(self.batch_times) / len(self.batch_times)
    
    def get_sentences_per_second(self) -> float:
        """Calculate processing speed"""
        total_time = self.get_total_time()
        if total_time == 0:
            return 0.0
        return self.total_sentences / total_time
    
    def get_cache_hit_rate(self) -> float:
        """Calculate cache hit rate as percentage"""
        if self.total_sentences == 0:
            return 0.0
        return (self.cache_hits / self.total_sentences) * 100
    
    def get_success_rate(self) -> float:
        """Calculate success rate as percentage"""
        if self.total_sentences == 0:
            return 100.0
        return ((self.total_sentences - self.validation_failures) / self.total_sentences) * 100
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Generate comprehensive performance summary
        
        Returns:
            Dictionary with all performance metrics
        """
        total_time = self.get_total_time()
        
        return {
            'speed': {
                'total_time': f"{total_time:.2f}s",
                'total_minutes': f"{total_time / 60:.1f}min",
                'sentences_per_second': f"{self.get_sentences_per_second():.1f}",
                'time_breakdown': {
                    'extraction': f"{self.extraction_time:.1f}s ({self.extraction_time/total_time*100:.0f}%)" if total_time > 0 else "0s",
                    'processing': f"{self.processing_time:.1f}s ({self.processing_time/total_time*100:.0f}%)" if total_time > 0 else "0s",
                    'validation': f"{self.validation_time:.1f}s ({self.validation_time/total_time*100:.0f}%)" if total_time > 0 else "0s"
                }
            },
            'efficiency': {
                'cache_hit_rate': f"{self.get_cache_hit_rate():.1f}%",
                'cache_hits': self.cache_hits,
                'api_calls': self.api_calls,
                'avg_batch_size': f"{self.get_avg_batch_size():.1f}",
                'avg_batch_time': f"{self.get_avg_batch_time():.2f}s",
                'tokens_per_sentence': f"{self.tokens_used / self.total_sentences:.0f}" if self.total_sentences > 0 else "0"
            },
            'quality': {
                'total_sentences': self.total_sentences,
                'direct_pass': f"{self.direct_sentences} ({self.direct_sentences / self.total_sentences * 100:.1f}%)" if self.total_sentences > 0 else "0",
                'ai_rewritten': f"{self.ai_rewrites} ({self.ai_rewrites / self.total_sentences * 100:.1f}%)" if self.total_sentences > 0 else "0",
                'mechanical_fallback': f"{self.mechanical_fallbacks} ({self.mechanical_fallbacks / self.total_sentences * 100:.1f}%)" if self.total_sentences > 0 else "0",
                'validation_failures': self.validation_failures,
                'success_rate': f"{self.get_success_rate():.1f}%"
            },
            'cost': {
                'estimated': f"${self.estimated_cost:.2f}",
                'actual': f"${self.actual_cost:.2f}",
                'cost_per_sentence': f"${self.actual_cost / self.total_sentences:.4f}" if self.total_sentences > 0 else "$0.0000"
            }
        }
    
    def print_summary(self):
        """Print formatted performance summary"""
        summary = self.get_summary()
        
        print("\n" + "="*70)
        print("PERFORMANCE METRICS SUMMARY")
        print("="*70)
        
        print(f"\n⏱️  SPEED METRICS")
        print(f"   Total Time:              {summary['speed']['total_time']} ({summary['speed']['total_minutes']})")
        print(f"   Processing Speed:        {summary['speed']['sentences_per_second']} sentences/sec")
        print(f"   Time Breakdown:")
        print(f"     - Extraction:          {summary['speed']['time_breakdown']['extraction']}")
        print(f"     - Processing:          {summary['speed']['time_breakdown']['processing']}")
        print(f"     - Validation:          {summary['speed']['time_breakdown']['validation']}")
        
        print(f"\n⚡ EFFICIENCY METRICS")
        print(f"   API Calls:               {summary['efficiency']['api_calls']}")
        print(f"   Avg Batch Size:          {summary['efficiency']['avg_batch_size']}")
        print(f"   Avg Batch Time:          {summary['efficiency']['avg_batch_time']}")
        print(f"   Cache Hit Rate:          {summary['efficiency']['cache_hit_rate']}")
        print(f"   Cache Hits:              {summary['efficiency']['cache_hits']}")
        print(f"   Tokens/Sentence:         {summary['efficiency']['tokens_per_sentence']}")
        
        print(f"\n✅ QUALITY METRICS")
        print(f"   Total Sentences:         {summary['quality']['total_sentences']}")
        print(f"   Direct Pass-through:     {summary['quality']['direct_pass']}")
        print(f"   AI Rewritten:            {summary['quality']['ai_rewritten']}")
        print(f"   Mechanical Fallback:     {summary['quality']['mechanical_fallback']}")
        print(f"   Success Rate:            {summary['quality']['success_rate']}")
        
        print(f"\n💰 COST METRICS")
        print(f"   Estimated Cost:          {summary['cost']['estimated']}")
        print(f"   Actual Cost:             {summary['cost']['actual']}")
        print(f"   Cost per Sentence:       {summary['cost']['cost_per_sentence']}")
        
        print("="*70 + "\n")
    
    def log_summary(self):
        """Log performance summary"""
        summary = self.get_summary()
        logger.info("Performance Summary:")
        logger.info(f"  Speed: {summary['speed']['total_time']}, {summary['speed']['sentences_per_second']} sent/sec")
        logger.info(f"  Efficiency: {summary['efficiency']['api_calls']} API calls, "
                   f"{summary['efficiency']['cache_hit_rate']} cache hit rate")
        logger.info(f"  Quality: {summary['quality']['success_rate']} success rate")
        logger.info(f"  Cost: {summary['cost']['actual']}")
