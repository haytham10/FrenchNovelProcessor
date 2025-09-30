"""
Quick Test for Gemini Integration
Tests the Gemini API connection and basic rewriting functionality
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.config_manager import ConfigManager
from src.rewriters.gemini_rewriter import GeminiRewriter


def test_gemini_integration():
    """Test Gemini API integration"""
    
    print("=" * 60)
    print("Gemini AI Integration Test")
    print("=" * 60)
    print()
    
    # Load config
    config = ConfigManager()
    
    # Check if Gemini is configured
    gemini_key = config.get_gemini_api_key()
    use_gemini = config.get_use_gemini_dev()
    
    print(f"Gemini API Key configured: {'Yes' if gemini_key else 'No'}")
    print(f"Use Gemini Dev flag: {use_gemini}")
    print(f"Should use Gemini: {config.should_use_gemini()}")
    print()
    
    if not gemini_key:
        print("❌ No Gemini API key found in config.ini")
        print()
        print("To set up Gemini:")
        print("1. Get API key from: https://aistudio.google.com/apikey")
        print("2. Add to config.ini under [Gemini] section")
        print("3. Set use_gemini_dev = true in [Processing] section")
        return False
    
    # Test API key
    print("Testing Gemini API key...")
    try:
        rewriter = GeminiRewriter(gemini_key, word_limit=8)
        is_valid, message = rewriter.validate_api_key()
        
        if is_valid:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing Gemini: {str(e)}")
        print()
        print("Make sure you've installed the package:")
        print("  .venv\\Scripts\\activate")
        print("  pip install google-genai")
        return False
    
    # Test sentence rewriting
    print()
    print("Testing sentence rewriting...")
    test_sentence = "Le chat noir dormait paisiblement sur le canapé rouge pendant que la pluie tombait doucement."
    print(f"Original ({len(test_sentence.split())} words):")
    print(f"  {test_sentence}")
    print()
    
    try:
        result = rewriter.rewrite_sentence(test_sentence)
        print(f"Rewritten into {len(result)} sentences:")
        for i, sent in enumerate(result, 1):
            word_count = len(sent.split())
            status = "✅" if word_count <= 8 else "⚠️"
            print(f"  {i}. {sent} ({word_count} words) {status}")
        
        print()
        print(f"Token usage: {rewriter.get_token_stats()}")
        print(f"Cost: ${rewriter.get_current_cost():.6f}")
        
    except Exception as e:
        print(f"❌ Rewriting failed: {str(e)}")
        return False
    
    print()
    print("=" * 60)
    print("✅ Gemini integration test PASSED!")
    print("=" * 60)
    print()
    print("Your system is ready to use Gemini for development.")
    print("The processor will automatically use Gemini when:")
    print("  • use_gemini_dev = true in config.ini")
    print("  • Processing mode is 'ai_rewrite'")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = test_gemini_integration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
