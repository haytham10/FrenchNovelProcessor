"""
French Novel Processor - Main Package
"""

__version__ = "2.0"
__author__ = "Haytham Mokhtari"
__client__ = "Stan Jones"

# Import key classes for easier access
from src.core.processor import NovelProcessor
from src.core.sentence_splitter import SentenceSplitter, ProcessingMode
from src.rewriters.ai_rewriter_backup_2 import AIRewriter
from src.rewriters.gemini_rewriter import GeminiRewriter
from src.utils.config_manager import ConfigManager
from src.utils.validator import SentenceValidator

__all__ = [
    'NovelProcessor',
    'SentenceSplitter',
    'ProcessingMode',
    'AIRewriter',
    'GeminiRewriter',
    'ConfigManager',
    'SentenceValidator',
]
