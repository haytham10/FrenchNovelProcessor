// French Novel Processor - JavaScript

let selectedFile = null;
let processingInterval = null;
let startTime = null;
let outputFiles = {};
const stageOrder = ['upload', 'analyzing', 'rewriting', 'export'];

// Load settings on page load
window.addEventListener('DOMContentLoaded', () => {
    loadSettings();
    setupFileInput();
    setupDragAndDrop();
    setupSettingPreview();
    setStage('upload');
    updateStatusCards();
});

// Load settings from server
async function loadSettings() {
    try {
        const response = await fetch('/api/settings');
        const settings = await response.json();
        
        // Update UI
        document.getElementById('apiKey').value = settings.api_key || '';
        document.getElementById('geminiApiKey').value = settings.gemini_api_key || '';
        document.getElementById('wordLimit').value = settings.word_limit;
        
        // AI Provider selection
        const aiProvider = settings.use_gemini_dev ? 'gemini' : 'openai';
        const providerRadio = document.querySelector(`input[name="aiProvider"][value="${aiProvider}"]`);
        if (providerRadio) providerRadio.checked = true;
        
        const modeRadio = document.querySelector(`input[name="processingMode"][value="${settings.processing_mode}"]`);
        if (modeRadio) modeRadio.checked = true;
        
        document.getElementById('showOriginal').checked = settings.show_original;
        document.getElementById('generateLog').checked = settings.generate_log;
        
        // Update API key statuses
        if (settings.api_key_configured) {
            showStatus('apiKeyStatus', '✓ API key configured', 'success');
        }
        if (settings.gemini_api_key_configured) {
            showStatus('geminiApiKeyStatus', '✓ API key configured', 'success');
        }
        
        updateAIProviderUI();
        updateStatusCards(settings);
    } catch (error) {
        console.error('Error loading settings:', error);
        updateStatusCards();
    }
}

// Save API key
async function saveApiKey() {
    const apiKey = document.getElementById('apiKey').value.trim();
    
    if (!apiKey) {
        showStatus('apiKeyStatus', 'Please enter an API key', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                api_key: apiKey,
                use_gemini_dev: false
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showStatus('apiKeyStatus', '✓ API key saved', 'success');
            updateStatusCards({ api_key_configured: true, api_key: apiKey });
        } else {
            showStatus('apiKeyStatus', `Error: ${result.error}`, 'error');
            updateStatusCards({ api_key_configured: false });
        }
    } catch (error) {
        showStatus('apiKeyStatus', `Error: ${error.message}`, 'error');
        updateStatusCards({ api_key_configured: false });
    }
}

// Save Gemini API key
async function saveGeminiApiKey() {
    const apiKey = document.getElementById('geminiApiKey').value.trim();
    
    if (!apiKey) {
        showStatus('geminiApiKeyStatus', 'Please enter an API key', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                gemini_api_key: apiKey,
                use_gemini_dev: true
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showStatus('geminiApiKeyStatus', '✓ API key saved', 'success');
            updateStatusCards({ gemini_api_key_configured: true });
        } else {
            showStatus('geminiApiKeyStatus', `Error: ${result.error}`, 'error');
            updateStatusCards({ gemini_api_key_configured: false });
        }
    } catch (error) {
        showStatus('geminiApiKeyStatus', `Error: ${error.message}`, 'error');
        updateStatusCards({ gemini_api_key_configured: false });
    }
}

// Test API key
async function testApiKey() {
    const apiKey = document.getElementById('apiKey').value.trim();
    
    if (!apiKey) {
        showStatus('apiKeyStatus', 'Please enter an API key', 'error');
        return;
    }
    
    showStatus('apiKeyStatus', 'Testing API key...', '');
    
    try {
        const response = await fetch('/api/test-api-key', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKey })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showStatus('apiKeyStatus', `✓ ${result.message}`, 'success');
            updateStatusCards({ api_key_configured: true });
        } else {
            showStatus('apiKeyStatus', `✗ ${result.message}`, 'error');
            updateStatusCards({ api_key_configured: false });
        }
    } catch (error) {
        showStatus('apiKeyStatus', `Error: ${error.message}`, 'error');
        updateStatusCards({ api_key_configured: false });
    }
}

// Test Gemini API key
async function testGeminiApiKey() {
    const apiKey = document.getElementById('geminiApiKey').value.trim();
    
    if (!apiKey) {
        showStatus('geminiApiKeyStatus', 'Please enter an API key', 'error');
        return;
    }
    
    showStatus('geminiApiKeyStatus', 'Testing API key...', '');
    
    try {
        const response = await fetch('/api/test-gemini-key', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKey })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showStatus('geminiApiKeyStatus', `✓ ${result.message}`, 'success');
            updateStatusCards({ gemini_api_key_configured: true });
        } else {
            showStatus('geminiApiKeyStatus', `✗ ${result.message}`, 'error');
            updateStatusCards({ gemini_api_key_configured: false });
        }
    } catch (error) {
        showStatus('geminiApiKeyStatus', `Error: ${error.message}`, 'error');
        updateStatusCards({ gemini_api_key_configured: false });
    }
}

// Toggle password visibility
function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    input.type = input.type === 'password' ? 'text' : 'password';
}

// Update AI Provider UI
function updateAIProviderUI() {
    const selectedProvider = document.querySelector('input[name="aiProvider"]:checked')?.value;
    const openaiSection = document.getElementById('openaiKeySection');
    const geminiSection = document.getElementById('geminiKeySection');
    
    if (selectedProvider === 'gemini') {
        openaiSection.style.display = 'none';
        geminiSection.style.display = 'block';
    } else {
        openaiSection.style.display = 'block';
        geminiSection.style.display = 'none';
    }
}

// Show status message
function showStatus(elementId, message, type) {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = `status-message ${type}`;
}

// Toggle settings panel
function toggleSettings() {
    const panel = document.getElementById('settingsPanel');
    const overlay = document.getElementById('settingsOverlay');
    if (!panel || !overlay) return;
    const shouldOpen = !panel.classList.contains('active');

    panel.classList.toggle('active', shouldOpen);
    overlay.classList.toggle('active', shouldOpen);
    panel.setAttribute('aria-hidden', (!shouldOpen).toString());
    document.body.classList.toggle('no-scroll', shouldOpen);
}

// Setup file input
function setupFileInput() {
    const fileInput = document.getElementById('fileInput');
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
}

// Setup drag and drop
function setupDragAndDrop() {
    const uploadArea = document.getElementById('uploadArea');
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        
        if (e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });
}

// Handle file selection
function handleFileSelect(file) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        alert('Please select a PDF file');
        return;
    }
    
    selectedFile = file;
    document.getElementById('fileInfo').textContent = `Selected: ${file.name} (${formatFileSize(file.size)})`;
    document.getElementById('processBtn').disabled = false;
    const resetBtn = document.getElementById('resetBtn');
    if (resetBtn) {
        resetBtn.style.display = 'inline-flex';
    }
}

// Format file size
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// Start processing
async function startProcessing() {
    if (!selectedFile) {
        alert('Please select a PDF file first');
        return;
    }
    
    // Get settings
    const wordLimit = parseInt(document.getElementById('wordLimit').value);
    const processingMode = document.querySelector('input[name="processingMode"]:checked').value;
    const showOriginal = document.getElementById('showOriginal').checked;
    const generateLog = document.getElementById('generateLog').checked;
    
    // Save settings
    try {
        await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                word_limit: wordLimit,
                processing_mode: processingMode,
                show_original: showOriginal,
                generate_log: generateLog
            })
        });
    } catch (error) {
        console.error('Error saving settings:', error);
    }
    
    // Prepare form data
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('word_limit', wordLimit);
    formData.append('processing_mode', processingMode);
    
    // Hide upload area, show progress
    document.getElementById('uploadArea').style.display = 'none';
    document.getElementById('processBtn').style.display = 'none';
    document.getElementById('progressSection').style.display = 'block';
    setStage('analyzing');
    document.getElementById('statusMessage').textContent = 'Uploading PDF and preparing sentences...';

    const resetBtn = document.getElementById('resetBtn');
    if (resetBtn) {
        resetBtn.style.display = 'none';
    }

    document.getElementById('processBtn').disabled = true;
    document.getElementById('progressFill').style.width = '0%';
    document.getElementById('progressText').textContent = '0%';
    
    startTime = Date.now();
    
    try {
        const response = await fetch('/api/process', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Start polling for status
            startStatusPolling();
        } else {
            showError(result.error);
        }
    } catch (error) {
        showError(error.message);
    }
}

// Start polling for status updates
function startStatusPolling() {
    processingInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            updateProgress(status);
            
            if (!status.is_processing) {
                clearInterval(processingInterval);
                
                if (status.error) {
                    showError(status.error);
                } else if (status.output_file) {
                    showResults(status);
                }
            }
        } catch (error) {
            console.error('Status polling error:', error);
        }
    }, 1000); // Poll every second
}

// Update progress display
function updateProgress(status) {
    // Update progress bar with smooth animation
    const progressFill = document.getElementById('progressFill');
    progressFill.style.width = status.progress + '%';
    
    // Add color indication based on progress
    if (status.progress < 30) {
        progressFill.style.background = 'linear-gradient(90deg, #3b82f6, #60a5fa)';
    } else if (status.progress < 80) {
        progressFill.style.background = 'linear-gradient(90deg, #8b5cf6, #a78bfa)';
    } else {
        progressFill.style.background = 'linear-gradient(90deg, #10b981, #34d399)';
    }
    
    document.getElementById('progressText').textContent = status.progress + '%';
    
    // Enhanced status message with better formatting
    let statusMsg = status.status_message || 'Processing...';
    
    // Add contextual info
    if (status.stats) {
        const total = status.stats.total_input_sentences || 0;
        const processed = (status.stats.direct_sentences || 0) + (status.stats.ai_rewritten || 0);
        if (total > 0 && processed < total) {
            statusMsg += ` (${processed}/${total} sentences)`;
        }
    }
    
    document.getElementById('statusMessage').textContent = statusMsg;
    
    // Update current sentence with truncation for long sentences
    if (status.current_sentence) {
        let sentence = status.current_sentence;
        if (sentence.length > 80) {
            sentence = sentence.substring(0, 77) + '...';
        }
        document.getElementById('currentSentence').textContent = `📝 ${sentence}`;
        document.getElementById('currentSentence').style.fontStyle = 'italic';
        document.getElementById('currentSentence').style.color = '#6b7280';
    }
    
    // Update stats with enhanced formatting
    if (status.stats) {
    document.getElementById('statTotal').textContent = status.stats.total_input_sentences || 0;
    document.getElementById('statDirect').textContent = status.stats.direct_sentences || 0;
    document.getElementById('statAI').textContent = status.stats.ai_rewritten || 0;
    document.getElementById('statAPICalls').textContent = status.stats.api_calls || 0;
        
    const cost = status.stats.cost || 0;
        const costElem = document.getElementById('statCost');
        costElem.textContent = '$' + cost.toFixed(4);
        
        // Color code cost based on amount
        if (cost === 0) {
            costElem.style.color = '#6b7280';
        } else if (cost < 0.50) {
            costElem.style.color = '#10b981';
        } else if (cost < 2.0) {
            costElem.style.color = '#f59e0b';
        } else {
            costElem.style.color = '#ef4444';
        }
        
        // Update time with ETA if possible
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const timeElem = document.getElementById('statTime');
        timeElem.textContent = formatTime(elapsed);
        
        // Calculate ETA if we have progress
        if (status.progress > 5 && status.progress < 95) {
            const rate = status.progress / elapsed;
            const remaining = (100 - status.progress) / rate;
            if (remaining > 0 && remaining < 3600) { // Less than 1 hour
                timeElem.textContent += ` (ETA: ${formatTime(Math.floor(remaining))})`;
            }
        }

        // Update stage indicator
        let nextStage = 'analyzing';
        if (status.stats.ai_rewritten > 0 || status.progress >= 30) {
            nextStage = 'rewriting';
        }
        if (status.progress >= 85 || status.stats.total_output_sentences) {
            nextStage = 'export';
        }
        if (status.progress <= 2) {
            nextStage = 'analyzing';
        }
        setStage(nextStage);
    }
}

// Format time
function formatTime(seconds) {
    if (seconds < 60) return seconds + 's';
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}m ${secs}s`;
}

function setStage(stage) {
    const chips = document.querySelectorAll('#stageChips .chip');
    if (!chips.length) return;

    const targetIndex = stageOrder.indexOf(stage);
    const effectiveIndex = targetIndex === -1 ? 0 : targetIndex;

    chips.forEach((chip) => {
        const chipStage = chip.dataset.stage;
        const chipIndex = stageOrder.indexOf(chipStage);
        chip.classList.toggle('current', chipStage === stageOrder[effectiveIndex]);
        chip.classList.toggle('active', chipIndex !== -1 && chipIndex <= effectiveIndex);
    });
}

function getCurrentSettingsFromUI() {
    const apiInput = document.getElementById('apiKey');
    const wordLimitInput = document.getElementById('wordLimit');
    const modeRadio = document.querySelector('input[name="processingMode"]:checked');
    const showOriginal = document.getElementById('showOriginal');
    const generateLog = document.getElementById('generateLog');

    return {
        api_key: apiInput ? apiInput.value.trim() : '',
        api_key_configured: apiInput ? apiInput.value.trim().length > 0 : false,
        word_limit: wordLimitInput ? parseInt(wordLimitInput.value, 10) || 8 : 8,
        processing_mode: modeRadio ? modeRadio.value : 'ai_rewrite',
        show_original: showOriginal ? showOriginal.checked : true,
        generate_log: generateLog ? generateLog.checked : true
    };
}

function updateStatusCards(patch = {}) {
    const baseState = getCurrentSettingsFromUI();
    const state = { ...baseState, ...patch };

    const apiStatusEl = document.getElementById('cardApiStatus');
    const apiMetaEl = document.getElementById('cardApiMeta');
    const modeValueEl = document.getElementById('cardModeValue');
    const modeMetaEl = document.getElementById('cardModeMeta');
    const modeIconEl = document.getElementById('cardModeIcon');
    const wordLimitEl = document.getElementById('cardWordLimit');
    const wordMetaEl = document.getElementById('cardWordMeta');

    if (!apiStatusEl) {
        return;
    }

    if (typeof patch.api_key_configured === 'boolean') {
        state.api_key_configured = patch.api_key_configured;
    }

    state.word_limit = parseInt(state.word_limit, 10) || 8;
    state.show_original = state.show_original === true || state.show_original === 'true';
    state.generate_log = state.generate_log === true || state.generate_log === 'true';

    const apiConfigured = state.api_key_configured || (state.api_key && state.api_key.length > 0);
    apiStatusEl.textContent = apiConfigured ? 'Ready to rewrite' : 'Not configured';
    if (apiMetaEl) {
        apiMetaEl.textContent = apiConfigured
            ? 'We\'ll use your key for AI rewriting.'
            : 'Save your OpenAI key to unlock AI rewriting.';
    }

    const modeValue = state.processing_mode === 'mechanical_chunking'
        ? 'Mechanical Chunking'
        : 'AI Rewriting';
    const modeMeta = state.processing_mode === 'mechanical_chunking'
        ? 'Splits sentences offline every few words.'
        : 'Uses GPT-4o-mini for natural French output.';
    const modeIcon = state.processing_mode === 'mechanical_chunking' ? '⚙️' : '🤖';
    if (modeValueEl) modeValueEl.textContent = modeValue;
    if (modeMetaEl) modeMetaEl.textContent = modeMeta;
    if (modeIconEl) modeIconEl.textContent = modeIcon;

    if (wordLimitEl) {
        wordLimitEl.textContent = `${state.word_limit || 8} words`;
    }
    if (wordMetaEl) {
        const originalFlag = state.show_original ? 'On' : 'Off';
        const logFlag = state.generate_log ? 'On' : 'Off';
        wordMetaEl.textContent = `Original sentences: ${originalFlag} • Log: ${logFlag}`;
    }
}

function setupSettingPreview() {
    const apiInput = document.getElementById('apiKey');
    const wordLimitInput = document.getElementById('wordLimit');
    const showOriginal = document.getElementById('showOriginal');
    const generateLog = document.getElementById('generateLog');
    const modeRadios = document.querySelectorAll('input[name="processingMode"]');

    if (apiInput) {
        apiInput.addEventListener('input', () => updateStatusCards());
    }
    if (wordLimitInput) {
        const clampWordLimit = () => {
            const min = parseInt(wordLimitInput.min, 10) || 5;
            const max = parseInt(wordLimitInput.max, 10) || 40;
            let value = parseInt(wordLimitInput.value, 10);
            if (Number.isNaN(value)) {
                value = min;
            }
            value = Math.min(Math.max(value, min), max);
            wordLimitInput.value = value;
            updateStatusCards();
        };
        wordLimitInput.addEventListener('change', clampWordLimit);
        wordLimitInput.addEventListener('blur', clampWordLimit);
    }
    if (showOriginal) {
        showOriginal.addEventListener('change', () => updateStatusCards());
    }
    if (generateLog) {
        generateLog.addEventListener('change', () => updateStatusCards());
    }
    modeRadios.forEach((radio) => {
        radio.addEventListener('change', () => updateStatusCards({ processing_mode: radio.value }));
    });
}

// Show results
function showResults(status) {
    document.getElementById('progressSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'block';
    setStage('export');
    
    // Store output file paths
    outputFiles.excel = status.output_file;
    outputFiles.csv = status.csv_file;
    
    // Generate summary
    const stats = status.stats;
    let summaryHTML = `
        <div class="summary-item">
            <span class="summary-label">Total sentences processed:</span>
            <span class="summary-value">${stats.total_input_sentences || 0}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">Output sentences:</span>
            <span class="summary-value">${stats.total_output_sentences || 0}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">Direct (≤8 words):</span>
            <span class="summary-value">${stats.direct_sentences || 0}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">AI-rewritten:</span>
            <span class="summary-value">${stats.ai_rewritten || 0}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">API calls made:</span>
            <span class="summary-value">${stats.api_calls || 0}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">Estimated cost:</span>
            <span class="summary-value">$${(stats.cost || 0).toFixed(2)}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">Processing time:</span>
            <span class="summary-value">${formatTime(Math.floor(stats.processing_time || 0))}</span>
        </div>
    `;
    
    // Add Google Sheets link if available
    if (status.google_sheets_url) {
        summaryHTML += `
        <div class="summary-item" style="grid-column: 1 / -1; background: linear-gradient(135deg, #34a853 0%, #0f9d58 100%); padding: 15px; border-radius: 8px; margin-top: 10px;">
            <span class="summary-label" style="color: white; font-weight: bold;">📊 Google Spreadsheet:</span>
            <a href="${status.google_sheets_url}" target="_blank" style="color: white; text-decoration: underline; font-weight: bold;">
                Open in Google Sheets →
            </a>
        </div>
        `;
    } else if (status.google_sheets_error) {
        summaryHTML += `
        <div class="summary-item" style="grid-column: 1 / -1; background: #fef3c7; padding: 15px; border-radius: 8px; margin-top: 10px;">
            <span class="summary-label" style="color: #92400e;">⚠️ Google Sheets:</span>
            <span style="color: #92400e;">Not created (${status.google_sheets_error})</span>
        </div>
        `;
    }
    
    document.getElementById('summaryGrid').innerHTML = summaryHTML;
    const resetBtn = document.getElementById('resetBtn');
    if (resetBtn) {
        resetBtn.style.display = 'none';
    }
}

// Show error
function showError(errorMessage) {
    document.getElementById('progressSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'block';
    document.getElementById('errorMessage').textContent = errorMessage;
    setStage('upload');
}

// Download file
function downloadFile(type) {
    const filename = type === 'excel' ? 
        outputFiles.excel.split(/[\\/]/).pop() : 
        outputFiles.csv.split(/[\\/]/).pop();
    
    window.location.href = `/api/download/${filename}`;
}

function clearSelectedFile() {
    const fileInput = document.getElementById('fileInput');
    selectedFile = null;
    if (fileInput) {
        fileInput.value = '';
    }
    document.getElementById('fileInfo').textContent = 'No file selected yet.';
    document.getElementById('processBtn').disabled = true;
    const resetBtn = document.getElementById('resetBtn');
    if (resetBtn) {
        resetBtn.style.display = 'none';
    }
    setStage('upload');
}

// Reset processor
function resetProcessor() {
    location.reload();
}
