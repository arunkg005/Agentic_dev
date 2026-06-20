const btn = document.getElementById('generate-btn');
const statusText = document.getElementById('status-text');
const pulseRing = document.getElementById('loading-ring');
const reportContent = document.getElementById('report-content');
const downloadGroup = document.getElementById('download-group');
const downloadMd = document.getElementById('download-md');
const downloadPdf = document.getElementById('download-pdf');
const downloadDocx = document.getElementById('download-docx');

// Chat UI references
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatSendBtn = document.getElementById('chat-send-btn');
const chatBox = document.getElementById('chat-box');

let currentMarkdown = "";

document.getElementById('campaign-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // UI Reset
    btn.disabled = true;
    pulseRing.classList.remove('hidden');
    downloadGroup.classList.add('hidden');
    downloadGroup.classList.remove('open');
    statusText.textContent = "Initializing planner...";
    statusText.style.color = '#34d399';
    reportContent.innerHTML = `<div class="empty-state">Generating strategy... Please wait.</div>`;

    // Reset Chat UI
    currentMarkdown = "";
    if (chatInput) {
        chatInput.disabled = true;
        chatInput.value = "";
        chatInput.placeholder = "Generate plan to unlock chat...";
    }
    if (chatSendBtn) chatSendBtn.disabled = true;
    if (chatBox) chatBox.innerHTML = `<div class="chat-message system">Generate a plan first to unlock the AI refinement assistant.</div>`;

    const data = {
        name: document.getElementById('name').value,
        topic: document.getElementById('topic').value,
        audience: document.getElementById('audience').value,
        reach: document.getElementById('reach').value,
        budget: document.getElementById('budget').value,
        duration: document.getElementById('duration').value,
        duration_unit: document.getElementById('duration_unit').value
    };

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (!response.body) throw new Error("ReadableStream not supported in this browser.");

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        let buffer = "";
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            
            // NDJSON comes with newlines
            let parts = buffer.split('\n');
            buffer = parts.pop(); // keep the last incomplete chunk in buffer

            for (const part of parts) {
                if (!part.trim()) continue;
                try {
                    const payload = JSON.parse(part);
                    if (payload.error) {
                        statusText.textContent = `Error: ${payload.error}`;
                        statusText.style.color = '#ef4444';
                        pulseRing.classList.add('hidden');
                        btn.disabled = false;
                        return;
                    }
                    
                    if (payload.status) {
                        statusText.textContent = payload.status;
                    }
                    
                    if (payload.html) {
                        reportContent.innerHTML = payload.html;
                    }

                    if (payload.file_path) {
                        // Success finish
                        downloadMd.setAttribute('data-url', '/' + payload.file_path);
                        if (payload.pdf_path) {
                            downloadPdf.setAttribute('data-url', '/' + payload.pdf_path);
                            downloadPdf.classList.remove('hidden');
                        } else {
                            downloadPdf.classList.add('hidden');
                        }
                        if (payload.docx_path) {
                            downloadDocx.setAttribute('data-url', '/' + payload.docx_path);
                            downloadDocx.classList.remove('hidden');
                        } else {
                            downloadDocx.classList.add('hidden');
                        }
                        downloadGroup.classList.remove('hidden');
                        pulseRing.classList.add('hidden');
                        btn.disabled = false;
                        statusText.style.color = '#10b981'; // Green for success

                        // Save Markdown to state
                        if (payload.markdown) {
                            currentMarkdown = payload.markdown;
                        }
                        
                        // Enable Chat
                        if (chatInput) {
                            chatInput.disabled = false;
                            chatInput.placeholder = "Ask to refine the plan...";
                        }
                        if (chatSendBtn) chatSendBtn.disabled = false;
                        if (chatBox) {
                            chatBox.innerHTML = `<div class="chat-message copilot">Hello! The campaign plan is generated successfully. What changes or refinements would you like me to make?</div>`;
                        }
                    }

                } catch (err) {
                    console.error("Parse error on chunk:", part, err);
                }
            }
        }
    } catch (error) {
        statusText.textContent = `Connection Error: ${error.message}`;
        statusText.style.color = '#ef4444';
        pulseRing.classList.add('hidden');
        btn.disabled = false;
    }
});

// User Guide Modal Interactivity
const infoBtn = document.getElementById('info-btn');
const guideModal = document.getElementById('guide-modal');
const closeModal = document.getElementById('close-modal');

if (infoBtn && guideModal && closeModal) {
    infoBtn.addEventListener('click', () => {
        guideModal.classList.remove('hidden');
    });

    closeModal.addEventListener('click', () => {
        guideModal.classList.add('hidden');
    });
}

// Copyable example values in the User Guide
document.querySelectorAll('.copyable').forEach(el => {
    el.addEventListener('click', () => {
        const textToCopy = el.getAttribute('data-copy');
        navigator.clipboard.writeText(textToCopy).then(() => {
            el.classList.add('copied');
            setTimeout(() => el.classList.remove('copied'), 1200);
        });
    });
});

// Dropdown Toggle & Window Click handlers
const dropdownTrigger = document.querySelector('.dropdown-trigger');
if (dropdownTrigger && downloadGroup) {
    dropdownTrigger.addEventListener('click', (e) => {
        e.stopPropagation();
        downloadGroup.classList.toggle('open');
    });
}

// Prevent dropdown menu clicks from closing the dropdown prematurely
const dropdownMenu = document.querySelector('.dropdown-menu');
if (dropdownMenu) {
    dropdownMenu.addEventListener('click', (e) => {
        e.stopPropagation();
    });
}

window.addEventListener('click', (e) => {
    if (guideModal && e.target === guideModal) {
        guideModal.classList.add('hidden');
    }
    if (downloadGroup && downloadGroup.classList.contains('open')) {
        downloadGroup.classList.remove('open');
    }
});

// Programmatic file download — fetches as blob and triggers a real save dialog
function triggerDownload(url) {
    fetch(url)
        .then(res => {
            if (!res.ok) throw new Error('File not found');
            return res.blob();
        })
        .then(blob => {
            const filename = url.split('/').pop();
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            setTimeout(() => {
                URL.revokeObjectURL(a.href);
                a.remove();
            }, 100);
        })
        .catch(err => console.error('Download failed:', err));
}

[downloadMd, downloadPdf, downloadDocx].forEach(link => {
    if (link) {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const url = link.getAttribute('data-url');
            if (url && url !== '#') {
                triggerDownload(url);
                downloadGroup.classList.remove('open');
            }
        });
    }
});

// Chat refinement submit handler
if (chatForm) {
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const userPrompt = chatInput.value.trim();
        if (!userPrompt || !currentMarkdown) return;
        
        // Add User Message bubble
        appendChatMessage("user", userPrompt);
        chatInput.value = "";
        
        // Disable chat input during refinement
        chatInput.disabled = true;
        chatSendBtn.disabled = true;
        
        // Add copilot typing bubble
        const typingBubble = appendChatMessage("copilot", "Refining campaign plan, please wait...");
        
        try {
            const response = await fetch('/api/refine', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    markdown: currentMarkdown,
                    prompt: userPrompt
                })
            });
            
            const result = await response.json();
            
            // Remove typing bubble
            typingBubble.remove();
            
            if (result.error) {
                appendChatMessage("error", `Error: ${result.error}`);
            } else {
                currentMarkdown = result.markdown;
                reportContent.innerHTML = result.html;
                
                // Update download paths
                downloadMd.setAttribute('data-url', '/' + result.file_path);
                if (result.pdf_path) {
                    downloadPdf.setAttribute('data-url', '/' + result.pdf_path);
                    downloadPdf.classList.remove('hidden');
                } else {
                    downloadPdf.classList.add('hidden');
                }
                if (result.docx_path) {
                    downloadDocx.setAttribute('data-url', '/' + result.docx_path);
                    downloadDocx.classList.remove('hidden');
                } else {
                    downloadDocx.classList.add('hidden');
                }
                
                appendChatMessage("copilot", "Campaign plan refined successfully! The preview and download files are updated.");
            }
        } catch (err) {
            typingBubble.remove();
            appendChatMessage("error", `Connection Error: ${err.message}`);
        } finally {
            chatInput.disabled = false;
            chatSendBtn.disabled = false;
            chatInput.focus();
        }
    });
}

function appendChatMessage(sender, text) {
    if (!chatBox) return null;
    const msg = document.createElement('div');
    msg.className = `chat-message ${sender}`;
    msg.innerText = text;
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
    return msg;
}

