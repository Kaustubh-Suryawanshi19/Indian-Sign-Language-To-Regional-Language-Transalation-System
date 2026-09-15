const POLL_INTERVAL = 400;
const TRANSLATION_TIMEOUT = 10000;

const videoFeed = document.getElementById('video-feed');
const signSequence = document.getElementById('sign-sequence');
const translationResult = document.getElementById('translation-result');
const translateBtn = document.getElementById('translate-btn');
const resetBtn = document.getElementById('reset-btn');
const languageSelect = document.getElementById('language');
const statusDisplay = document.getElementById('status-display');
const detectionBtn = document.getElementById('toggle-detection-btn');

let detectedSigns = [];
let isTranslating = false;
let pollTimer = null;

function updateStatus(message) {
    if (statusDisplay) statusDisplay.textContent = message;
}

function updateSignDisplay() {
    if (!signSequence) return;
    signSequence.textContent = detectedSigns.length
        ? detectedSigns.join(' → ')
        : 'No signs detected';
}

async function fetchJSON(url, options = {}) {
    const response = await fetch(url, options);
    let data = {};
    try { data = await response.json(); } catch (_) {}
    if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
    return data;
}

async function checkForDetections() {
    try {
        const data = await fetchJSON('/api/process');
        detectedSigns = data.sequence || [];
        updateSignDisplay();
        if (data.error) updateStatus(`Detection error: ${data.error}`);
        else if (data.detection_active) updateStatus(detectedSigns.length ? `Detected: ${detectedSigns.join(', ')}` : 'Waiting for signs…');
        else updateStatus('Detection paused');
        if (detectionBtn) detectionBtn.textContent = data.detection_active ? 'Stop Detection' : 'Start Detection';
    } catch (error) {
        updateStatus(error.message);
    }
}

function startPolling() {
    if (pollTimer) clearInterval(pollTimer);
    pollTimer = setInterval(checkForDetections, POLL_INTERVAL);
    checkForDetections();
}

async function handleDetectionToggle() {
    if (!detectionBtn) return;
    detectionBtn.disabled = true;
    try {
        const data = await fetchJSON('/api/toggle_detection', { method: 'POST' });
        detectionBtn.textContent = data.detection_active ? 'Stop Detection' : 'Start Detection';
        updateStatus(data.detection_active ? 'Camera detection started' : 'Detection stopped');
    } catch (error) {
        updateStatus(error.message);
    } finally {
        detectionBtn.disabled = false;
    }
}

async function handleTranslation() {
    if (isTranslating || detectedSigns.length === 0) return;
    isTranslating = true;
    translateBtn.disabled = true;
    translationResult.textContent = 'Translating…';
    updateStatus('Generating sentence…');

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), TRANSLATION_TIMEOUT);
    try {
        const data = await fetchJSON('/api/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ signs: [...detectedSigns], lang: languageSelect.value }),
            signal: controller.signal,
        });
        translationResult.textContent = data.translation;
        updateStatus(`Translation complete (${data.method})`);
    } catch (error) {
        translationResult.textContent = error.name === 'AbortError' ? 'Translation timed out.' : error.message;
        updateStatus('Translation failed');
    } finally {
        clearTimeout(timeout);
        isTranslating = false;
        translateBtn.disabled = false;
    }
}

async function handleReset() {
    resetBtn.disabled = true;
    try {
        await fetchJSON('/api/reset', { method: 'POST' });
        detectedSigns = [];
        updateSignDisplay();
        if (translationResult) translationResult.textContent = '';
        updateStatus('Sequence reset');
    } catch (error) {
        updateStatus(error.message);
    } finally {
        resetBtn.disabled = false;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    translateBtn?.addEventListener('click', handleTranslation);
    resetBtn?.addEventListener('click', handleReset);
    detectionBtn?.addEventListener('click', handleDetectionToggle);
    startPolling();
});
