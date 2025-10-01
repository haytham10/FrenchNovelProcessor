"""
Lightweight text pre-cleaning utilities to reduce OCR artifacts before AI rewriting.

Functions here should be conservative and language-aware for French text.
"""

import re

SENTENCE_BREAK_TOKEN = "<SNT_BREAK>"


def clean_text_for_ai(text: str) -> str:
    """
    Clean common OCR artifacts to help AI produce better, grammatical outputs.

    - De-hyphenate across line breaks: "philo-\n sophe" -> "philosophe"
    - Normalize French apostrophes/quotes: ’ → ', “ ” → ", « » → "
    - Fix space before apostrophes: "l ' été" -> "l'été"
    - Collapse excessive whitespace, unify line breaks to single spaces

    Args:
        text: Raw text

    Returns:
        Cleaned text string
    """
    if not text:
        return ""

    t = text

    # Normalize newlines
    t = t.replace("\r\n", "\n").replace("\r", "\n")

    # 1) De-hyphenate words split across line breaks or spaces (common in OCR)
    #    Pattern: word-\s*\n\s*word  OR  word-\s+word
    t = re.sub(r"(\w)[\-‑]\s*\n\s*(\w)", r"\1\2", t)  # hyphen + newline
    t = re.sub(r"(\w)[\-‑]\s+(\w)", r"\1\2", t)        # hyphen + spaces

    # 2) Normalize quotes and apostrophes
    t = t.replace("’", "'")
    t = t.replace("“", '"').replace("”", '"')
    t = t.replace("«", '"').replace("»", '"')

    # 3) Fix spaced apostrophes in French elisions: d ' accord -> d'accord
    #    Handle common single-letter elisions and a few two-letter ones
    t = re.sub(r"\b([dljmtscnqD L J M T S C N Q])\s*'\s+", lambda m: m.group(1).strip().lower() + "'", t)
    # Also fix l ’ espace with fancy apostrophes already normalized
    t = re.sub(r"\b([A-Za-z])\s+'\s+([A-Za-z])", r"\1'\2", t)

    # 4) Preserve meaningful line breaks while flattening layout wraps
    #    - Keep double (or more) breaks as explicit sentence boundaries via sentinel
    #    - Join single line wraps that continue with lowercase/digit characters
    t = t.replace("\u00A0", " ")  # non-breaking space

    # Join line wraps when next line starts with lowercase letter or digit
    t = re.sub(r"\n(?=[a-zà-öø-ÿ0-9'\-])", " ", t)

    # Convert remaining newline runs to sentinel separators
    t = re.sub(r"\n+", f" {SENTENCE_BREAK_TOKEN} ", t)

    # Collapse remaining multiple spaces
    t = re.sub(r"\s+", " ", t)
    t = t.strip()

    return t
