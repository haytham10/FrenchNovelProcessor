# French Novel Processor - Quick Reference Card

## 🎯 What Does This Tool Do?

**Analyzes French text sentence by sentence:**
- ✅ Sentences ≤8 words → Added directly to Google Sheet
- ✂️ Sentences >8 words → Rewritten into multiple sentences, each ≤8 words

**Example:**
```
📥 Input: "Pierre marche lentement dans le grand parc avec son chien noir." (10 words)

📤 Output:
   ✓ "Pierre marche dans le grand parc." (6 words)
   ✓ "Il est avec son chien noir." (6 words)
```

---

## ⚙️ Settings

| Setting | Default | What It Does |
|---------|---------|--------------|
| **Word Limit** | 8 | Sentences with this many words or fewer pass through unchanged. Longer sentences are rewritten. |
| **Processing Mode** | AI Rewrite | How to handle long sentences: AI (smart) or Mechanical (simple chunks) |
| **API Provider** | Gemini (dev) | Which AI to use: Gemini (free) or OpenAI (paid, better quality) |
| **Show Original** | Yes | Include original sentence in output for comparison |

---

## 📊 How It Works

### Step 1: Analyze Sentence
```
Word count = count words in sentence
```

### Step 2: Process
```
IF word count ≤ word_limit (default: 8):
    → Add sentence to output (Direct)
ELSE:
    → Rewrite into multiple sentences (each ≤ word_limit)
    → Each new sentence:
       ✓ Must be ≤ word_limit words
       ✓ Preserves original meaning
       ✓ Reuses original words
       ✓ Maintains French grammar
```

### Step 3: Output
All sentences (direct + rewritten) → Google Sheet / Excel / CSV

---

## 📝 Examples by Word Count

### ✅ 3 words (Direct)
```
Input:  "Je marche vite." (3 ≤ 8)
Output: "Je marche vite."
```

### ✅ 8 words (Direct - at limit)
```
Input:  "Je marche lentement dans le grand parc municipal." (8 ≤ 8)
Output: "Je marche lentement dans le grand parc municipal."
```

### ✂️ 10 words (Rewritten)
```
Input:  "Le chat noir dort paisiblement sur le canapé près de la fenêtre." (11 > 8)
Output: "Le chat noir dort sur le canapé." (7 words)
        "Le canapé est près de la fenêtre." (7 words)
```

### ✂️ 20 words (Rewritten - multiple)
```
Input:  "Le professeur a expliqué que la théorie de la relativité était très difficile à comprendre pour les jeunes étudiants." (20 > 8)
Output: "Le professeur a expliqué la théorie." (6 words)
        "La relativité est difficile à comprendre." (6 words)
        "C'est dur pour les jeunes étudiants." (6 words)
```

---

## 🔧 Word Limit Configuration

You can change the default 8-word limit:

| Use Case | Suggested Limit | Why |
|----------|----------------|-----|
| **Children's books** | 5 words | Very simple sentences |
| **Language learners** | 8 words | Balance of simplicity and meaning (default) |
| **Intermediate readers** | 12 words | More natural sentences |
| **Advanced users** | 15 words | Keep longer complex ideas together |

**To change:** Settings → "Word Limit per Sentence" → Enter number → Save

---

## 📈 Statistics

After processing, you'll see:

| Stat | Meaning |
|------|---------|
| **Direct sentences** | Sentences that were ≤ word_limit (added as-is) |
| **AI-rewritten** | Sentences that were > word_limit (rewritten by AI) |
| **Mechanical-chunked** | Sentences split by simple word division (AI fallback) |
| **Total sentences** | All sentences processed |
| **API calls** | Number of AI requests made |
| **Cost estimate** | Approximate cost in USD |

**Example output:**
```
📊 Statistics:
   - Total sentences: 1,000
   - Direct (≤8 words): 350 (35%)
   - AI-rewritten (>8 words): 600 (60%)
   - Mechanical chunks: 50 (5%)
   - API calls: 650
   - Cost: $0.13
```

---

## 💡 Tips & Tricks

### 🎯 For Best Results
1. **Use AI mode** - Much better grammar than mechanical chunking
2. **Start with word_limit=8** - Good balance for most use cases
3. **Enable "Show Original"** - Compare before/after to verify quality
4. **Check the log** - Review which sentences were rewritten

### 💰 To Save Money
1. **Use Gemini (dev mode)** - Free tier: 15 requests/min, 1500/day
2. **Higher word limit** - Fewer sentences need rewriting
3. **Mechanical mode** - Free but lower quality

### 📚 For Language Learning
1. **Word limit = 8** - Simple enough to understand
2. **Show Original = Yes** - Learn by comparison
3. **Export to Excel** - Review offline, add notes

### 🚀 For Large Documents
1. **Use batch processing** - Much faster
2. **Gemini for free** - No cost concerns
3. **Check progress** - Web interface shows real-time updates

---

## ❓ FAQ

**Q: Why 8 words?**  
A: Research shows 8 words is ideal for language learners - long enough to be meaningful, short enough to be simple.

**Q: Can I change the word limit?**  
A: Yes! Settings → Word Limit → Any number you want.

**Q: What if AI fails?**  
A: Automatic fallback to mechanical chunking (simple word-based splitting).

**Q: Do short sentences get changed?**  
A: No! If a sentence is ≤ word_limit, it's added to output unchanged.

**Q: Is the meaning preserved?**  
A: Yes! The AI is instructed to preserve meaning and reuse original words.

**Q: What about grammar?**  
A: AI mode maintains proper French grammar. Mechanical mode may create fragments.

**Q: How much does it cost?**  
A: Gemini (free tier): $0. OpenAI: ~$0.50-1.00 per novel.

**Q: Can I process offline?**  
A: Yes, use Mechanical mode (no API needed).

---

## 🚦 Quick Start

1. **Launch:** Run `scripts\run_application.bat`
2. **Open:** Browser → http://localhost:5000
3. **Configure:** Settings → Add API key (Gemini or OpenAI)
4. **Upload:** Drag & drop your PDF
5. **Set limit:** Word Limit = 8 (or your preference)
6. **Process:** Click "Process PDF"
7. **Download:** Excel, CSV, or upload to Google Sheets

**That's it!** Your French text is now simplified into sentences of 8 words or fewer. 🎉

---

## 📖 Algorithm Summary

```
FOR EACH sentence IN book:
    word_count = count_words(sentence)
    
    IF word_count <= word_limit:
        ADD sentence to output  (unchanged)
    ELSE:
        REWRITE sentence into multiple sentences
        WHERE each new sentence <= word_limit
        AND meaning is preserved
        AND original words are reused
        AND French grammar is correct
        
        ADD new sentences to output

EXPORT all sentences to Google Sheets/Excel/CSV
```

Simple as that! 📊✨

---

## 📚 More Info

- **Full Documentation:** `docs/ALGORITHM.md`
- **Setup Guide:** `README.md`
- **Changelog:** `docs/CHANGELOG.md`
- **Troubleshooting:** `README.md` → Troubleshooting section

---

*French Novel Processor v2.1 - Making French literature accessible, one sentence at a time.* 🇫🇷📖✨
