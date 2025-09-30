"""
Test Script for French Novel Processor
Quick tests to verify basic functionality
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from src.utils.config_manager import ConfigManager
        from src.rewriters.ai_rewriter import AIRewriter
        from src.utils.validator import SentenceValidator
        from src.core.sentence_splitter import SentenceSplitter, ProcessingMode
        from src.core.processor import NovelProcessor
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_config_manager():
    """Test configuration manager"""
    print("\nTesting ConfigManager...")
    try:
        from src.utils.config_manager import ConfigManager
        
        # Create test config
        config = ConfigManager("test_config.ini")
        config.set_word_limit(10)
        config.set_processing_mode("ai_rewrite")
        
        # Read back
        assert config.get_word_limit() == 10
        assert config.get_processing_mode() == "ai_rewrite"
        
        # Cleanup
        if os.path.exists("test_config.ini"):
            os.remove("test_config.ini")
        
        print("✓ ConfigManager working correctly")
        return True
    except Exception as e:
        print(f"✗ ConfigManager error: {e}")
        return False


def test_validator():
    """Test sentence validator"""
    print("\nTesting SentenceValidator...")
    try:
        from src.utils.validator import SentenceValidator
        
        validator = SentenceValidator(word_limit=8)
        
        # Test word counting
        assert validator.count_words("one two three") == 3
        
        # Test validation
        valid_sentences = ["Un deux trois", "Quatre cinq six sept huit"]
        is_valid, word_counts = validator.validate_word_count(valid_sentences)
        assert is_valid == True
        
        invalid_sentences = ["Un deux trois quatre cinq six sept huit neuf"]
        is_valid, word_counts = validator.validate_word_count(invalid_sentences)
        assert is_valid == False
        
        print("✓ SentenceValidator working correctly")
        return True
    except Exception as e:
        print(f"✗ SentenceValidator error: {e}")
        return False


def test_sentence_splitter_mechanical():
    """Test sentence splitter in mechanical mode"""
    print("\nTesting SentenceSplitter (mechanical mode)...")
    try:
        from src.core.sentence_splitter import SentenceSplitter, ProcessingMode
        
        splitter = SentenceSplitter(
            word_limit=8,
            mode=ProcessingMode.MECHANICAL_CHUNKING
        )
        
        # Test short sentence (should pass through)
        result = splitter.process_sentence("Le chat dort.")
        assert result.method == "Direct"
        assert len(result.output_sentences) == 1
        
        # Test long sentence (should be chunked)
        long_sentence = "Le chat noir dormait paisiblement sur le canapé confortable près de la fenêtre"
        result = splitter.process_sentence(long_sentence)
        assert result.method == "Mechanical-Chunked"
        assert len(result.output_sentences) > 1
        
        # Verify all chunks are within limit
        for sentence in result.output_sentences:
            assert len(sentence.split()) <= 8
        
        print("✓ SentenceSplitter (mechanical) working correctly")
        return True
    except Exception as e:
        print(f"✗ SentenceSplitter error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_rewriter_mock():
    """Test AI rewriter initialization (without actual API call)"""
    print("\nTesting AIRewriter initialization...")
    try:
        from src.rewriters.ai_rewriter import AIRewriter
        
        # Create with dummy key (won't make actual calls)
        rewriter = AIRewriter(api_key="test_key", word_limit=8)
        
        # Test word counting
        assert rewriter.count_words("one two three") == 3
        
        # Test prompt generation
        system_prompt = rewriter.get_system_prompt()
        assert "French" in system_prompt
        assert str(8) in system_prompt
        
        user_prompt = rewriter.get_user_prompt("Test sentence")
        assert "Test sentence" in user_prompt
        
        print("✓ AIRewriter initialization working correctly")
        return True
    except Exception as e:
        print(f"✗ AIRewriter error: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("French Novel Processor - Test Suite")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_config_manager,
        test_validator,
        test_sentence_splitter_mechanical,
        test_ai_rewriter_mock
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)
    
    if all(results):
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
