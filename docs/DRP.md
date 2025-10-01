# **Development Requirements Plan (DRP)**
## French Novel Processor - AI-Powered Sentence Rewriting Amendment

**Client:** Stan Jones  
**Developer:** Haytham Mokhtari  
**Project Type:** Amendment to existing tool  
**Project Duration:** 2-3 days  
**Budget:** $125 fixed  
**Original Tool:** French Novel Processor (delivered Sep 29, 2025)  
**Location:** "../'French Novel Sentence Splitter'"
**Start Date:** 30-09-2025  
**Delivery Date:** 03-10-2025

---

## **1. Project Overview**

### **1.1 Current State**
The existing French Novel Processor splits long sentences into mechanical 8-word chunks without regard for grammar or meaning:

**Example:**
- **Input:** "Le chat noir dormait paisiblement sur le canapé confortable près de la fenêtre"
- **Current Output:** 
  - "Le chat noir dormait paisiblement sur"
  - "le canapé confortable près de la"

### **1.2 Desired State**
Intelligently rewrite long sentences into grammatically correct shorter sentences while preserving meaning and using original words:

**Example:**
- **Input:** "Le chat noir dormait paisiblement sur le canapé confortable près de la fenêtre"
- **New Output:** 
  - "Le chat noir dormait sur le canapé."
  - "Le canapé était confortable et près de la fenêtre."

### **1.3 Amendment Scope**
Replace mechanical chunking algorithm with AI-powered intelligent sentence rewriting while maintaining all existing functionality (PDF processing, OCR, Google Sheets export, UI, etc.)

---

## **2. Technical Requirements**

### **2.1 AI Integration**

#### **Primary Option: OpenAI GPT-5 nano**
- **API:** OpenAI Chat Completions API
- **Model:** `gpt-5-nano` (fastest, cheapest, excellent for French)
- **Estimated cost per novel:** $0.50-1 depending on length
- **Processing time:** 10-15 minutes for 350-page novel

#### **Backup Option: Google Gemini**
- **API:** Gemini 2.5 Flash Lite
- **Free tier available**
- **Similar pricing and performance**

#### **API Key Management**
- User provides their own API key
- Stored securely in local config file (not hardcoded)
- Easy setup through UI or config file
- API key validation on first run

### **2.2 Sentence Analysis Logic**

```
FOR EACH sentence in novel:
    word_count = count_words(sentence)
    
    IF word_count <= specified_limit (default: 8):
        add_to_sheet(sentence)
    
    ELSE:
        rewritten_sentences = ai_rewrite(sentence, word_limit)
        validate_rewritten_sentences(original, rewritten_sentences)
        add_to_sheet(rewritten_sentences)
```

### **2.3 AI Prompt Engineering**

#### **System Prompt:**
```
You are a French language expert specializing in sentence simplification. 
Your task is to rewrite long French sentences into shorter, grammatically 
correct sentences while preserving the original meaning and using as many 
original words as possible.

Rules:
1. Each new sentence must be {word_limit} words or fewer
2. Maintain proper French grammar and syntax
3. Preserve the original meaning completely
4. Reuse original words whenever possible
5. Ensure natural, fluent French
6. Output only the rewritten sentences, one per line
7. Do not add explanations or commentary
```

#### **User Prompt Template:**
```
Rewrite this French sentence into multiple shorter sentences, 
each containing {word_limit} words or fewer:

"{original_sentence}"

Output format: One sentence per line.
```

### **2.4 Quality Validation**

After AI rewriting, implement checks:
- **Word count validation:** Each output sentence ≤ specified limit
- **Language detection:** Verify output is French (using langdetect library)
- **Content preservation:** Check that key nouns/verbs from original appear in output
- **Fallback:** If AI fails or produces invalid output, mark sentence for manual review

---

## **3. Input Requirements**

### **3.1 Existing Inputs (Unchanged)**
- PDF files from Google Drive
- Word limit specification (default: 8 words)

### **3.2 New Inputs**
- **OpenAI API Key** (required)
  - Entered through UI settings panel
  - Or via `config.ini` file
  - Validated on first use
- **Processing Mode Selection:**
  - Option 1: AI-powered rewriting (new default)
  - Option 2: Mechanical chunking (legacy mode)

---

## **4. Output Requirements**

### **4.1 Google Sheets Output (Enhanced)**

**Existing columns:**
- Column A: Row number
- Column B: Sentence text

**New columns:**
- Column C: Original sentence (if rewritten by AI)
- Column D: Rewrite method (Direct | AI-Rewritten | Failed)
- Column E: Word count

**New tab: "Processing Log"**
- Sentences that required AI rewriting
- Any failed rewrites
- API call count and estimated cost
- Total processing time

### **4.2 CSV Backup (Enhanced)**
Same structure as Google Sheets output

### **4.3 Processing Summary**
Display at end of processing:
```
✅ Processing Complete!

Total sentences processed: 4,237
├─ Direct (≤8 words): 1,856
├─ AI-rewritten: 2,381
└─ Failed rewrites: 0

API calls made: 2,381
Estimated cost: $3.20
Processing time: 18 minutes

Google Sheet: [link]
CSV backup: output/novel_processed_20250930_143022.csv
```

---

## **5. User Interface Updates**

### **5.1 Settings Panel (New)**

Add settings section to existing UI:

```
┌─────────────────────────────────────┐
│ SETTINGS                            │
├─────────────────────────────────────┤
│ OpenAI API Key:                     │
│ [sk-...........................] 💾 │
│ [Test Connection]                   │
│                                     │
│ Processing Mode:                    │
│ ○ AI-Powered Rewriting (recommended)│
│ ○ Mechanical Chunking (legacy)      │
│                                     │
│ Maximum words per sentence: [8]     │
│                                     │
│ ☑ Show original sentences in output│
│ ☑ Generate processing log          │
└─────────────────────────────────────┘
```

### **5.2 Progress Tracking (Enhanced)**

Update existing progress display:

```
Processing: Chapter_5.pdf

━━━━━━━━━━━━━━━━━━ 67% (142/211 pages)

Current sentence: "Marie regardait par la fenêtre..."
├─ Original: 14 words
└─ Rewriting with AI... ⏳

Sentences processed: 3,847
├─ Direct: 1,623
├─ AI-rewritten: 2,224
└─ API calls: 2,224

Estimated cost so far: $2.10
Time elapsed: 12m 34s
```

### **5.3 First-Time Setup Wizard**

Add one-time setup for API key:

```
┌─────────────────────────────────────┐
│ 🔑 OpenAI API Key Required          │
├─────────────────────────────────────┤
│ To use AI-powered rewriting, you    │
│ need an OpenAI API key.              │
│                                      │
│ Don't have one? Get it here:         │
│ [Open OpenAI Platform] 🔗            │
│                                      │
│ Already have a key? Enter it below:  │
│ [____________________________]       │
│                                      │
│ [Skip - Use Legacy Mode] [Continue]  │
└─────────────────────────────────────┘
```

---

## **6. Implementation Details**

### **6.1 New/Modified Files**

```
FrenchNovelProcessor/
├── run_application.bat          # Unchanged
├── setup.bat                    # Updated (new dependencies)
├── config.ini                   # NEW - Stores API key
├── processor.py                 # Modified - Add mode selection
├── sentence_splitter.py         # Modified - Add AI rewriting
├── ai_rewriter.py               # NEW - OpenAI integration
├── validator.py                 # NEW - Quality checks
├── web_interface/
│   ├── app.py                   # Modified - Settings panel
│   ├── templates/
│   │   └── index.html           # Modified - New UI elements
│   └── static/
│       └── styles.css           # Modified - Settings styling
├── output/                      # Unchanged
├── README.md                    # Updated - API key setup
└── requirements.txt             # Updated - Add openai library
```

### **6.2 New Dependencies**

Add to `requirements.txt`:
```
openai==1.12.0              # OpenAI API client
langdetect==1.0.9           # Language validation
tenacity==8.2.3             # Retry logic for API calls
```

### **6.3 Code Architecture**

#### **ai_rewriter.py**
```python
class AIRewriter:
    def __init__(self, api_key, word_limit=8):
        self.client = OpenAI(api_key=api_key)
        self.word_limit = word_limit
    
    def rewrite_sentence(self, sentence):
        """
        Rewrite a long sentence into shorter ones using AI.
        Returns: list of rewritten sentences
        """
        # System prompt
        # User prompt with sentence
        # API call with retry logic
        # Parse and validate response
        # Return list of sentences
    
    def validate_api_key(self):
        """Test if API key is valid"""
        # Make test API call
        # Return True/False
    
    def estimate_cost(self, text):
        """Estimate API cost for processing text"""
        # Count tokens
        # Calculate cost based on pricing
```

#### **validator.py**
```python
class SentenceValidator:
    def validate_rewrite(self, original, rewritten_list, word_limit):
        """
        Validate that rewritten sentences meet criteria
        Returns: (is_valid, error_message)
        """
        # Check word count of each sentence
        # Verify language is French
        # Check for content preservation
        # Return validation result
    
    def check_content_preservation(self, original, rewritten_list):
        """Check if key words are preserved"""
        # Extract key nouns/verbs from original
        # Check if present in rewritten versions
        # Return similarity score
```

### **6.4 Error Handling**

#### **API Errors**
- **Invalid API key:** Show clear error message with setup link
- **Rate limit exceeded:** Pause processing, show wait time, auto-retry
- **Network error:** Retry 3 times with exponential backoff
- **Insufficient credits:** Show error with link to billing page

#### **Quality Errors**
- **AI returns sentence >word_limit:** Try again with stricter prompt
- **AI returns non-French text:** Try again, fallback to mechanical chunking
- **AI fails after 3 attempts:** Mark sentence, continue processing, log failure

#### **Fallback Strategy**
If AI fails for any sentence after retries:
1. Log the failure in processing log
2. Use legacy mechanical chunking for that sentence
3. Mark it clearly in output for manual review
4. Continue processing remaining sentences

---

## **7. API Cost Management**

### **7.1 Cost Estimation**

**OpenAI GPT-5 nano Pricing:**
- Input: $0.05 per 1M tokens (~70% cheaper than GPT-4o-mini)
- Output: $0.40 per 1M tokens (~33% cheaper than GPT-4o-mini)

**Typical 350-page novel:**
- Estimated sentences needing rewrite: ~2,500
- Average tokens per sentence: 30 input, 40 output
- Total tokens: 75,000 input + 100,000 output
- **Cost: ~$0.50-$1.00 per novel**

### **7.2 Cost Display**

Show cost estimates:
- **Before processing:** "Estimated cost: $0.50-1"
- **During processing:** "Current cost: $0.35"
- **After processing:** "Total cost: $0.75"

### **7.3 Cost Optimization**

- Batch multiple sentences per API call when possible
- Cache common rewrites
- Only send to AI if sentence >word_limit
- Use GPT-5 nano (fastest & cheapest)

---

## **8. Setup & Installation**

### **8.1 Updated Setup Process**

**Step 1: Run setup.bat** (updated)
- Installs new dependencies (openai, langdetect, tenacity)
- Everything else same as before

**Step 2: Get OpenAI API Key** (new)
- Guide user to platform.openai.com
- Show how to create API key
- Where to add payment method

**Step 3: Enter API Key**
- Through UI settings panel (easiest)
- Or edit config.ini file manually

**Step 4: Test Connection**
- Click "Test Connection" button
- Validates key works
- Shows account credit balance if possible

**Step 5: Use Tool**
- Same as before - drag PDF, set word limit, process

### **8.2 Backwards Compatibility**

Users can still use legacy mechanical chunking:
- Select "Mechanical Chunking" mode in settings
- No API key required for legacy mode
- Original functionality preserved

### **8.3 Setup Time**

- **With API key ready:** 2 minutes (just enter key)
- **Without API key:** 10 minutes (create OpenAI account, add payment, get key)

---

## **9. Testing Plan**

### **9.1 AI Quality Testing**

Test with various sentence types:

**Simple sentences:**
- "Le chat dort sur le tapis rouge dans le salon."
- Expected: Clean split, maintains meaning

**Complex sentences:**
- "Bien que Marie fût fatiguée après sa longue journée de travail, elle décida de sortir avec ses amis pour célébrer son anniversaire."
- Expected: Proper handling of subjunctive, time clauses

**Dialogue:**
- "« Je ne comprends pas pourquoi tu continues à faire cela », dit Pierre avec frustration."
- Expected: Preserves quotation marks, attribution

**Technical terms:**
- Sentences with names, dates, numbers
- Expected: Preserves exact terms

### **9.2 API Integration Testing**

- Valid API key → Successful processing
- Invalid API key → Clear error message
- Rate limit → Proper retry behavior
- Network timeout → Retry with backoff
- Insufficient credits → Informative error

### **9.3 Cost Accuracy Testing**

- Process sample novel
- Compare estimated vs actual cost (from OpenAI dashboard)
- Ensure estimates are accurate within 10%

### **9.4 Performance Testing**

- **350-page novel:** Should complete in 15-25 minutes
- **Memory usage:** Should stay under 1.5GB
- **API call efficiency:** Minimize redundant calls

### **9.5 Validation Testing**

- All output sentences ≤ word limit
- All output is French
- Meaning preserved (manual review of sample)
- No data loss (sentence count makes sense)

---

## **10. Documentation Updates**

### **10.1 Updated README.md**

Add new sections:
- **API Key Setup:** Step-by-step with screenshots
- **Processing Modes:** Explain AI vs. mechanical
- **Cost Information:** What to expect
- **Troubleshooting:** Common API errors

### **10.2 Updated QuickStart.pdf**

Add pages for:
- Getting OpenAI API key
- Entering key in settings
- Understanding cost estimates
- Interpreting processing log

### **10.3 New Video Walkthrough**

Record new 7-10 minute video covering:
1. What's new in this version (0:00-1:00)
2. Getting OpenAI API key (1:00-3:00)
3. Setting up the tool (3:00-4:30)
4. Processing a sample novel (4:30-7:00)
5. Understanding the output (7:00-9:00)
6. Cost management tips (9:00-10:00)

---

## **11. Deliverables**

### **11.1 Updated Tool Package**

```
FrenchNovelProcessor_v2/
├── run_application.bat
├── run_tool.bat
├── setup.bat
├── [All updated Python files]
├── config.ini.template
├── README.md (updated)
├── CHANGELOG.md (new - documents changes)
├── output/
└── requirements.txt (updated)
```

### **11.2 Documentation**

- Updated README.md with API setup
- Updated QuickStart.pdf
- New video walkthrough (7-10 min)
- CHANGELOG.md explaining what's new

### **11.3 Migration Guide**

For users with existing tool:
- What's changed
- How to update
- How to keep using legacy mode if preferred

---

## **12. Success Criteria**

### **12.1 Functional Requirements**

✅ **Must Have:**
1. AI correctly rewrites long sentences into shorter ones
2. All output sentences ≤ specified word limit
3. Meaning and grammar preserved in French
4. API key setup works smoothly
5. Cost estimates are accurate
6. Error handling works for all API issues
7. Legacy mode still available

✅ **Should Have:**
1. Processing time <25 minutes for 350-page novel
2. Cost per novel <$5
3. Less than 1% failed rewrites
4. Setup time <10 minutes for new users

✅ **Nice to Have:**
1. Batch processing optimization
2. Rewrite quality metrics
3. Comparison view (before/after)

### **12.2 User Experience**

- Clear instructions for API setup
- Helpful error messages
- Progress visibility during processing
- Cost transparency
- Easy switching between modes

---

## **13. Known Limitations**

### **13.1 Technical Limitations**

- **Internet required:** AI rewriting needs active connection
- **API costs:** Ongoing cost per novel ($2-5)
- **Processing time:** Slower than mechanical chunking (15-20 min vs. 5 min)
- **API dependency:** Relies on OpenAI service availability

### **13.2 Quality Limitations**

- AI may occasionally miss nuance in complex literary language
- Very technical or archaic French may not rewrite perfectly
- Idiomatic expressions might be lost in simplification
- Poetry/verse will likely lose artistic structure

### **13.3 Cost Limitations**

- User must have OpenAI account with payment method
- Large novels (500+ pages) may cost $6-8
- Frequent processing requires budget consideration

---

## **14. Future Enhancements (Out of Scope)**

Not included in this amendment but possible future additions:

- **Local AI option:** Run smaller model locally (no API costs)
- **Multiple AI providers:** Claude, Mistral, etc.
- **Quality scoring:** Rate rewrite quality automatically
- **Manual editing:** UI for adjusting AI output
- **Batch processing:** Process multiple novels at once
- **Rewrite caching:** Save common rewrites to reduce costs

---

## **15. Timeline Breakdown**

### **Day 1: Core AI Integration (8 hours)**
- Set up OpenAI API client
- Implement ai_rewriter.py
- Build prompt engineering system
- Add retry/error handling logic
- Initial testing with sample sentences

### **Day 2: UI & Validation (8 hours)**
- Add settings panel to web interface
- Implement validator.py
- Add config.ini management
- Build cost estimation
- Update progress tracking
- Integration testing

### **Day 3: Polish & Documentation (6 hours)**
- Full novel testing
- Fix any bugs
- Update README and QuickStart PDF
- Record new video walkthrough
- Final testing
- Package and deliver

**Total: ~22 hours over 2-3 days**

---

## **16. Client Approval Checkpoints**

### **Checkpoint 1: Before Starting**
- Confirm DRP aligns with expectations
- Agree on $125 budget
- Clarify any questions about API costs

### **Checkpoint 2: Day 2 Morning**
- Share screenshot of AI rewriting in action
- Show sample before/after sentences
- Confirm quality meets expectations

### **Checkpoint 3: Delivery**
- Walkthrough session demonstrating new features
- Process sample novel together
- Answer any questions
- Get final approval

---

## **17. Support & Maintenance**

### **17.1 Included Support (30 Days)**

- Bug fixes for AI integration
- Help with API key setup
- Troubleshooting API errors
- Minor prompt adjustments for quality
- Documentation clarifications

### **17.2 Not Included**

- OpenAI API costs (client's responsibility)
- Major feature additions
- Support for other AI providers
- Custom rewriting logic beyond original spec

### **17.3 Support Channels**

- Upwork messages (primary)
- Response time: Within 12 hours on weekdays
- Screen sharing for complex issues

---

## **18. Payment Terms**

- **Amendment cost:** $125 fixed price
- **Payment trigger:** Upon delivery and approval
- **Original tool:** Already paid ($75)
- **No refunds** on original tool (as agreed)
- **Amendment guarantee:** Full functionality as specified or refund of $125

---

## **19. Risk Management**

### **19.1 Technical Risks**

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenAI API changes | High | Use stable API version, abstract API calls |
| Rate limiting issues | Medium | Implement retry logic, batch processing |
| Quality inconsistency | Medium | Validation checks, fallback to legacy mode |
| Cost overruns | Low | Accurate token counting, cost warnings |

### **19.2 User Experience Risks**

| Risk | Impact | Mitigation |
|------|--------|------------|
| API setup too complex | Medium | Detailed guide, video, first-run wizard |
| Cost concerns | Medium | Clear estimates, transparency, legacy option |
| Slower processing | Low | Progress visibility, accurate time estimates |

---

## **20. Acceptance Criteria**

**The amendment will be considered complete when:**

1. ✅ User can enter OpenAI API key through UI
2. ✅ Tool validates API key on first use
3. ✅ Long sentences (>8 words) are intelligently rewritten by AI
4. ✅ Short sentences (≤8 words) pass through unchanged
5. ✅ All output sentences meet word limit requirement
6. ✅ Output maintains French grammar and meaning
7. ✅ Cost estimates display accurately
8. ✅ Processing log shows what was rewritten
9. ✅ Legacy mechanical chunking mode still available
10. ✅ Error handling works for common API issues
11. ✅ Documentation updated with API setup instructions
12. ✅ Video walkthrough demonstrates new features
13. ✅ Sample novel processes successfully
14. ✅ Client can use tool independently after walkthrough

---

**Client Sign-off:**

_By proceeding with this amendment, both parties agree to the scope, deliverables, timeline, and budget outlined above._

**Stan Jones:** _________________ Date: _______

**Haytham Mokhtari:** _________________ Date: _______

---

## **Appendix A: Example Transformations**

### **Example 1: Simple Sentence**
```
Original (12 words):
"Le petit garçon jouait avec son chien dans le parc ensoleillé."

AI Rewrite:
1. "Le petit garçon jouait avec son chien." (8 words)
2. "Ils étaient dans le parc ensoleillé." (6 words)
```

### **Example 2: Complex Sentence**
```
Original (18 words):
"Après avoir terminé ses devoirs, Marie a décidé de sortir pour rencontrer ses amis au café habituel."

AI Rewrite:
1. "Marie a terminé ses devoirs." (5 words)
2. "Elle a décidé de sortir ensuite." (6 words)
3. "Elle voulait rencontrer ses amis au café." (7 words)
```

### **Example 3: Dialogue**
```
Original (15 words):
"« Je pense que nous devrions partir maintenant », dit Pierre en regardant sa montre nerveusement."

AI Rewrite:
1. "« Je pense que nous devrions partir », dit Pierre." (8 words)
2. "Il regardait sa montre nerveusement." (5 words)
```

---

## **Appendix B: API Setup Guide (Quick Reference)**

### **Step-by-Step:**

1. **Go to:** https://platform.openai.com
2. **Sign up** or log in
3. **Add payment method:** Billing → Payment methods
4. **Create API key:** API keys → Create new secret key
5. **Copy key** (starts with `sk-...`)
6. **In tool:** Settings → Paste API key → Test Connection
7. **Process your first novel!**

**Cost expectation:** $5-10 in credits should process 2-3 novels.