"""
French Novel Processor v2.0 - Demo Script
==========================================

This script demonstrates the core functionality without requiring
a full PDF or actual API calls (uses mock mode for testing).
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.sentence_splitter import SentenceSplitter, ProcessingMode
from src.utils.validator import SentenceValidator
from src.utils.config_manager import ConfigManager
import time


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")


def demo_mechanical_mode():
    """Demonstrate mechanical chunking (legacy mode)"""
    print_header("DEMO 1: Mechanical Chunking Mode")
    
    # Sample French sentences
    sentences = [
        "Le chat dort.",  # Short sentence (won't be split)
        "Le chat noir dormait paisiblement sur le canapé confortable près de la fenêtre ouverte.",
        "Marie regardait par la fenêtre tout en pensant à son voyage de demain matin à Paris."
    ]
    
    splitter = SentenceSplitter(mode=ProcessingMode.MECHANICAL_CHUNKING, word_limit=8)
    
    for i, sentence in enumerate(sentences, 1):
        print(f"Sentence {i}: {sentence}")
        print(f"Word count: {len(sentence.split())} words\n")
        
        result = splitter.process_sentence(sentence)
        
        print(f"Method: {result.method}")
        print(f"Output ({len(result.output_sentences)} sentences):")
        for j, output in enumerate(result.output_sentences, 1):
            word_count = len(output.split())
            print(f"  {j}. {output} ({word_count} words)")
        print("\n" + "-"*60)


def demo_config_manager():
    """Demonstrate configuration management"""
    print_header("DEMO 2: Configuration Manager")
    
    config = ConfigManager()
    
    # Show current settings
    print("Default Settings:")
    print(f"  Word Limit: {config.get_word_limit()}")
    print(f"  Processing Mode: {config.get_processing_mode()}")
    api_key = config.get_api_key()
    print(f"  API Key Set: {'Yes' if api_key else 'No'}")
    
    # Test setting/getting values
    print("\nSetting word limit to 10...")
    config.set_word_limit(10)
    print(f"  New word limit: {config.get_word_limit()}")
    
    print("\nSetting processing mode to AI...")
    config.set_processing_mode("ai")
    print(f"  New mode: {config.get_processing_mode()}")


def demo_validator():
    """Demonstrate sentence validation"""
    print_header("DEMO 3: Sentence Validation")
    
    validator = SentenceValidator(word_limit=8)
    
    # Test cases
    test_cases = [
        {
            "original": "Le chat noir dormait paisiblement sur le canapé confortable.",
            "rewritten": ["Le chat noir dormait paisiblement.", "Il était sur le canapé confortable."],
            "expected": True
        },
        {
            "original": "Marie mange une pomme.",
            "rewritten": ["This is not French at all."],
            "expected": False
        },
        {
            "original": "Le soleil brille aujourd'hui.",
            "rewritten": ["Le soleil brille aujourd'hui magnifiquement avec splendeur."],
            "expected": False  # Exceeds word limit
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test Case {i}:")
        print(f"  Original: {test['original']}")
        print(f"  Rewritten: {test['rewritten']}")
        
        is_valid, message, details = validator.validate_rewrite(
            test['original'],
            test['rewritten']
        )
        
        print(f"  Valid: {'✓' if is_valid else '✗'}")
        if not is_valid:
            print(f"  Reason: {message}")
        print()


def demo_cost_estimation():
    """Demonstrate cost estimation"""
    print_header("DEMO 4: Cost Estimation")
    
    try:
        from src.rewriters.ai_rewriter import AIRewriter
        
        # Create rewriter with dummy key for estimation only
        rewriter = AIRewriter(api_key="dummy_key_for_demo")
        
        # Sample text
        sample_text = """
        Le chat noir dormait paisiblement sur le canapé confortable près de la fenêtre.
        Marie regardait par la fenêtre tout en pensant à son voyage.
        Pierre mangeait un croissant en lisant le journal du matin.
        """
        
        sentences = [s.strip() for s in sample_text.strip().split('\n') if s.strip()]
        long_sentences = [s for s in sentences if len(s.split()) > 8]
        
        print(f"Sample text analysis:")
        print(f"  Total sentences: {len(sentences)}")
        print(f"  Sentences needing rewrite: {len(long_sentences)}")
        print()
        
        # Estimate tokens
        total_input_tokens = sum(rewriter.estimate_tokens(s) for s in long_sentences)
        # Assume output is 1.5x input (conservative)
        total_output_tokens = int(total_input_tokens * 1.5)
        
        print(f"Token estimation:")
        print(f"  Input tokens: ~{total_input_tokens}")
        print(f"  Output tokens: ~{total_output_tokens}")
        print()
        
        # Calculate cost
        input_cost = (total_input_tokens / 1_000_000) * rewriter.input_price_per_1m
        output_cost = (total_output_tokens / 1_000_000) * rewriter.output_price_per_1m
        total_cost = input_cost + output_cost
        
        print(f"Cost estimation:")
        print(f"  Input cost: ${input_cost:.4f}")
        print(f"  Output cost: ${output_cost:.4f}")
        print(f"  Total cost: ${total_cost:.4f}")
        print()
        
        # Extrapolate to full novel
        print("For a typical 350-page novel (~2,500 sentences):")
        scale_factor = 2500 / len(long_sentences)
        novel_cost = total_cost * scale_factor
        print(f"  Estimated cost: ${novel_cost:.2f}")
        
    except Exception as e:
        print(f"Error in cost estimation demo: {e}")


def demo_progress_tracking():
    """Demonstrate batch processing and statistics"""
    print_header("DEMO 5: Batch Processing & Statistics")
    
    # Create splitter
    splitter = SentenceSplitter(
        mode=ProcessingMode.MECHANICAL_CHUNKING,
        word_limit=8
    )
    
    # Simulate processing multiple sentences
    sentences = [
        "Le chat dort sur le tapis.",
        "Marie mange une pomme rouge et juteuse dans le jardin ensoleillé.",
        "Le soleil brille aujourd'hui.",
        "Pierre travaille dans son bureau confortable avec vue sur la mer.",
        "Il fait beau temps."
    ]
    
    print(f"Processing {len(sentences)} sentences:\n")
    
    results = []
    for i, sentence in enumerate(sentences, 1):
        result = splitter.process_sentence(sentence)
        results.append(result)
        word_count = len(sentence.split())
        status = "✓" if result.success else "✗"
        print(f"{status} Sentence {i} ({word_count} words) → {len(result.output_sentences)} output sentence(s)")
    
    print(f"\n📊 Processing Statistics:")
    stats = splitter.stats
    print(f"  Total sentences: {stats['total_sentences']}")
    print(f"  Direct (≤8 words): {stats['direct_sentences']}")
    print(f"  Chunked: {stats['mechanical_chunked']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Total output: {sum(len(r.output_sentences) for r in results)} sentences")


def main():
    """Run all demos"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║    FRENCH NOVEL PROCESSOR v2.0 - DEMONSTRATION SUITE      ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    try:
        demo_mechanical_mode()
        demo_config_manager()
        demo_validator()
        demo_cost_estimation()
        demo_progress_tracking()
        
        print_header("DEMO COMPLETE")
        print("✓ All demonstrations completed successfully!")
        print("\nTo start the web interface, run: run_application.bat")
        print("To process actual novels, you'll need an OpenAI API key.")
        print("\nSee README.md for setup instructions.")
        
    except Exception as e:
        print(f"\n✗ Demo error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
