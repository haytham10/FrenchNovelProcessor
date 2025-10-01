# French Novel Processor - Core Algorithm

## Overview
The French Novel Processor analyzes text sentence by sentence and ensures all output sentences meet a specified word limit (default: 8 words).

## Algorithm Flow

### Step 1: Extract Sentences
1. Extract text from PDF (using PyPDF2 or OCR if needed)
2. Split text into individual sentences using French sentence boundaries
3. Clean OCR artifacts and normalize text

### Step 2: Analyze Each Sentence
For each sentence in the book:

#### Case A: Sentence is within word limit (≤8 words by default)
```
Input: "Je marche vite." (3 words)
Action: Add directly to output
Output: "Je marche vite."
```

#### Case B: Sentence exceeds word limit (>8 words by default)
```
Input: "Je marche dans le parc et je suis très fatigué maintenant." (12 words)
Action: Rewrite into multiple sentences, each ≤8 words
Output: 
  - "Je marche dans le parc." (6 words)
  - "Je suis très fatigué maintenant." (5 words)
```

## Rewriting Rules

When a sentence exceeds the word limit, it must be rewritten according to these rules:

### 1. Word Limit Constraint (CRITICAL)
- **Each new sentence MUST be ≤ word_limit words** (default: 8)
- Count words carefully: `len(sentence.split())`
- This is a hard constraint - violations will trigger fallback to mechanical chunking

### 2. Meaning Preservation (CRITICAL)
- The overall meaning must be retained completely
- Do not add new information
- Do not remove information
- Do not change facts or relationships

### 3. Word Reuse (CRITICAL)
- Reuse as many original words as possible
- Prefer keeping the original vocabulary
- Only add minimal function words if needed for grammar:
  - Articles: le, la, les, un, une, des
  - Prepositions: de, à, dans, pour, avec, etc.
  - Pronouns: je, tu, il, elle, nous, vous, ils, elles, etc.
  
### 4. Grammar and Style
- Maintain proper French grammar and syntax
- Keep the same tone and style as the original
- Ensure natural, fluent French
- Sentences should sound like they could appear in the original text

## Processing Modes

### AI Rewriting Mode (Default)
Uses Gemini AI or OpenAI to intelligently rewrite long sentences:
- Analyzes sentence structure
- Finds natural breaking points (commas, conjunctions, relative clauses)
- Creates grammatically correct shorter sentences
- Preserves meaning and reuses original words
- If the first rewrite fails validation (for example, a sentence exceeds the word limit),
  the system automatically performs a **strict retry** using Structured Outputs to force
  compliance with the word limit before considering a mechanical fallback
- Falls back to mechanical chunking only after the strict retry fails

### Mechanical Chunking Mode (Fallback)
Simple word-based splitting:
```python
def mechanical_chunk(sentence, word_limit=8):
    words = sentence.split()
    chunks = []
    for i in range(0, len(words), word_limit):
        chunk = ' '.join(words[i:i + word_limit])
        chunks.append(chunk)
    return chunks
```

**Example:**
```
Input: "Je marche dans le parc et je suis très fatigué maintenant." (12 words)
Output (mechanical):
  - "Je marche dans le parc et je" (7 words)
  - "suis très fatigué maintenant." (4 words)
```

Note: Mechanical chunking may create grammatically incorrect fragments but guarantees word limit compliance.

## Configuration

### Word Limit
- Default: **8 words**
- Configurable via settings
- Can be changed to any positive integer
- Recommended range: 5-15 words

### API Selection
- **Gemini AI** (Development): Free tier, 15 requests/minute
- **OpenAI GPT-5 nano** (Production): Paid, higher quality

## Output Format

### Google Sheets
All processed sentences (both direct and rewritten) are added to Google Sheets with:
- Original sentence (if enabled)
- Output sentence(s)
- Processing method (Direct, AI-Rewritten, Mechanical-Chunked)
- Word count
- Status

### CSV/Excel
Same data available in CSV and Excel formats for offline use.

## Validation

After AI rewriting, each output is validated:

1. **Word Count Check**: Each sentence ≤ word_limit
2. **Meaning Check**: Preserved content and relationships
3. **Word Reuse Check**: Uses original words (with allowed exceptions)
4. **Grammar Check**: Proper French syntax

If validation fails → fallback to mechanical chunking.

## Examples

### Example 1: Short Sentence (Direct Pass-Through)
```
Input: "Il dort." (2 words)
Word Limit: 8
Processing: Direct (already ≤8 words)
Output: "Il dort."
```

### Example 2: Long Sentence (AI Rewriting)
```
Input: "Pierre marche lentement dans le grand parc municipal avec son chien noir." (12 words)
Word Limit: 8
Processing: AI-Rewritten
Output: 
  - "Pierre marche lentement dans le parc." (6 words)
  - "Il est avec son chien noir." (6 words)
```

### Example 3: Very Long Sentence (AI Rewriting)
```
Input: "Le professeur a expliqué que la théorie de la relativité était difficile à comprendre pour les étudiants qui n'avaient pas de bonnes bases en mathématiques et en physique." (30 words)
Word Limit: 8
Processing: AI-Rewritten
Output:
  - "Le professeur a expliqué la théorie." (6 words)
  - "La relativité est difficile à comprendre." (6 words)
  - "Les étudiants manquent de bases." (5 words)
  - "Ils ont besoin de mathématiques." (5 words)
  - "Ils ont besoin de physique." (5 words)
```

### Example 4: Complex Sentence (Fallback to Mechanical)
```
Input: "Un deux trois quatre cinq six sept huit neuf dix onze douze." (12 words)
Word Limit: 8
Processing: Mechanical-Chunked (AI validation failed)
Output:
  - "Un deux trois quatre cinq six sept huit" (8 words)
  - "neuf dix onze douze." (4 words)
```

## Performance

### AI Mode
- **Speed**: ~1-2 seconds per sentence (single), ~0.1s per sentence (batch of 20)
- **Quality**: High - grammatically correct, natural French
- **Cost**: Small per sentence (Gemini: $0.0001, OpenAI: $0.0005)

### Mechanical Mode
- **Speed**: Instant
- **Quality**: Low - may create sentence fragments
- **Cost**: Free

## Statistics Tracked

For each processing run:
- Total sentences processed
- Direct sentences (≤ word_limit)
- AI-rewritten sentences (> word_limit, AI successful)
- Mechanical-chunked sentences (> word_limit, AI failed/disabled)
- Failed sentences (errors)
- API calls made
- Tokens used (input/output)
- Estimated cost

## Summary

The algorithm ensures that **every sentence in the output has exactly word_limit words or fewer** by:
1. Passing through short sentences unchanged
2. Rewriting long sentences into multiple shorter sentences
3. Preserving meaning and reusing original words
4. Maintaining proper French grammar
5. Falling back to mechanical chunking if needed

This produces a Google Sheet where each row contains a sentence with ≤ word_limit words, making it ideal for language learning, reading practice, or text simplification.
