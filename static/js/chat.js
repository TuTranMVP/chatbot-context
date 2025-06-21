/**
 * 🤖 BotQA Chat Interface JavaScript
 * Modern chatbot client with template system
 * Author: TutranMVP Team
 * Version: 2.0
 * Dependencies: None (Vanilla JS)
 */

// ============================================================================
// 🌐 GLOBAL VARIABLES & STATE
// ============================================================================

let isThinking = false;
let templates = {};

// ============================================================================
// 🚀 INITIALIZATION & EVENT LISTENERS
// ============================================================================

/**
 * Initialize the chat application
 */
function initializeChat() {
    console.log('🚀 Initializing BotQA Chat Interface...');

    loadTemplates();
    setupEventListeners();
    setupTemplateButtons();
    setupControlHandlers();

    // Focus input on page load
    document.getElementById('message-input')?.focus();

    console.log('✅ Chat interface initialized successfully!');
}

/**
 * Load templates from API
 */
async function loadTemplates() {
    try {
        const response = await fetch('/api/templates');
        const data = await response.json();

        if (data.success) {
            templates = data.templates;
            console.log('📋 Templates loaded:', Object.keys(templates).length);
        } else {
            console.error('❌ Failed to load templates:', data.error);
        }
    } catch (error) {
        console.error('❌ Error loading templates:', error);
        updateStatus('⚠️ Không thể tải templates', 'error');
    }
}

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    // Auto-resize textarea
    const messageInput = document.getElementById('message-input');
    if (messageInput) {
        messageInput.addEventListener('input', autoResizeTextarea);
        messageInput.addEventListener('keydown', handleKeyPress);
    }

    // Temperature slider
    const tempSlider = document.getElementById('temperature');
    if (tempSlider) {
        tempSlider.addEventListener('input', function () {
            const tempValue = document.getElementById('temp-value');
            if (tempValue) {
                tempValue.textContent = this.value;
            }
        });
    }
}

/**
 * Setup template button handlers
 */
function setupTemplateButtons() {
    document.querySelectorAll('.template-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            handleTemplateClick(this);
        });

        // Add keyboard support
        btn.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handleTemplateClick(this);
            }
        });
    });
}

/**
 * Setup control handlers (temperature slider, etc.)
 */
function setupControlHandlers() {
    // Temperature slider
    const tempSlider = document.getElementById('temperature');
    if (tempSlider) {
        tempSlider.addEventListener('input', function () {
            const tempValue = document.getElementById('temp-value');
            if (tempValue) {
                tempValue.textContent = this.value;
            }
        });
    }
}

// ============================================================================
// 🎯 TEMPLATE HANDLING
// ============================================================================

/**
 * Handle template button clicks
 * @param {HTMLElement} btn - The clicked template button
 */
function handleTemplateClick(btn) {
    const templateType = btn.dataset.template;
    const template = templates[templateType];

    if (template && template.example) {
        const input = document.getElementById('message-input');
        if (input) {
            input.value = template.example;
            input.focus();
            autoResizeTextarea();
        }

        // Add visual feedback
        btn.style.transform = 'scale(0.95)';
        setTimeout(() => {
            btn.style.transform = '';
        }, 150);

        console.log(`📋 Template selected: ${templateType}`);
    } else {
        // Fallback examples if template not loaded
        const fallbackExamples = {
            'analysis': 'Phân tích hiệu suất website của công ty tôi',
            'steps': 'Hướng dẫn cách tạo chatbot bằng Python',
            'summary': 'Tóm tắt cuộc họp team development hôm nay',
            'qa': 'Python là gì và tại sao nên học ngôn ngữ này?'
        };

        const input = document.getElementById('message-input');
        if (input && fallbackExamples[templateType]) {
            input.value = fallbackExamples[templateType];
            input.focus();
            autoResizeTextarea();
        }
    }
}

// ============================================================================
// 💬 MESSAGE HANDLING
// ============================================================================

/**
 * Add message to chat with improved animations
 * @param {string} content - Message content
 * @param {string} type - Message type (user, bot, template, error, system)
 * @param {boolean} isHTML - Whether content contains HTML
 */
function addMessage(content, type = 'user', isHTML = false) {
    const messagesContainer = document.getElementById('chat-messages');
    if (!messagesContainer) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    if (isHTML) {
        contentDiv.innerHTML = content;
    } else {
        contentDiv.textContent = content;
    }

    messageDiv.appendChild(contentDiv);

    // Add with fade-in animation
    messageDiv.style.opacity = '0';
    messageDiv.style.transform = 'translateY(20px)';
    messagesContainer.appendChild(messageDiv);

    // Trigger animation
    requestAnimationFrame(() => {
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0)';
    });

    // Auto scroll to bottom with smooth behavior
    setTimeout(() => {
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);
}

/**
 * Send message to chatbot
 */
async function sendMessage() {
    if (isThinking) return;

    const input = document.getElementById('message-input');
    const message = input?.value.trim();

    if (!message) {
        // Add shake animation to input if empty
        if (input) {
            input.style.animation = 'shake 0.5s ease-in-out';
            setTimeout(() => {
                input.style.animation = '';
            }, 500);
        }
        return;
    }

    const temperature = parseFloat(document.getElementById('temperature')?.value || '0.3');
    const maxTokens = parseInt(document.getElementById('max-tokens')?.value || '800');

    // Add user message
    addMessage(`👤 Bạn: ${message}`, 'user');

    // Clear input and reset height
    if (input) {
        input.value = '';
        autoResizeTextarea();
    }

    // Show thinking state
    isThinking = true;
    showTyping(true);

    const sendBtn = document.getElementById('send-btn');
    if (sendBtn) {
        sendBtn.disabled = true;
        sendBtn.innerHTML = '⏳ Đang gửi...';
    }

    updateStatus('🤔 Đang suy nghĩ...', 'thinking');

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                temperature: temperature,
                max_tokens: maxTokens
            })
        });

        const data = await response.json();

        if (data.success) {
            // Show template being used
            addMessage(`🎨 Template: ${data.template}`, 'template');

            // Show bot response
            addMessage(`🤖 Bot: ${data.response}`, 'bot');

            updateStatus('✅ Sẵn sàng', 'ready');
        } else {
            addMessage(`❌ Lỗi: ${data.error}`, 'error');
            updateStatus('❌ Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        console.error('❌ Send message error:', error);
        addMessage(`❌ Lỗi kết nối: ${error.message}`, 'error');
        updateStatus('❌ Lỗi kết nối', 'error');
    } finally {
        // Reset state
        isThinking = false;
        showTyping(false);

        if (sendBtn) {
            sendBtn.disabled = false;
            sendBtn.innerHTML = '📤 Gửi';
        }

        // Focus back to input
        if (input) {
            input.value = '';
            input.focus();
        }
    }
}

// ============================================================================
// 🎨 UI UTILITIES & ANIMATIONS
// ============================================================================

/**
 * Show/hide typing indicator with null safety
 * @param {boolean} show - Whether to show typing indicator
 */
function showTyping(show) {
    // Ensure typing indicator exists
    const indicator = ensureTypingIndicator();
    const messagesContainer = document.getElementById('chat-messages');

    // Safety check for null elements
    if (!indicator || !messagesContainer) {
        console.warn('⚠️ Typing indicator or messages container not found');
        return;
    }

    if (show) {
        indicator.style.display = 'block';
        // Check if indicator is not already appended to avoid duplication
        if (!messagesContainer.contains(indicator)) {
            messagesContainer.appendChild(indicator);
        }
    } else {
        indicator.style.display = 'none';
        // Remove indicator from messages container if it exists there
        if (messagesContainer.contains(indicator)) {
            messagesContainer.removeChild(indicator);
        }
    }

    // Smooth scroll to bottom
    setTimeout(() => {
        messagesContainer.scrollTo({
            top: messagesContainer.scrollHeight,
            behavior: 'smooth'
        });
    }, 50);
}

/**
 * Ensure typing indicator exists
 * @returns {HTMLElement} The typing indicator element
 */
function ensureTypingIndicator() {
    let indicator = document.getElementById('typing-indicator');
    if (!indicator) {
        // Recreate typing indicator if it doesn't exist
        indicator = document.createElement('div');
        indicator.id = 'typing-indicator';
        indicator.className = 'typing-indicator';
        indicator.style.display = 'none';
        indicator.innerHTML = `
            <div class="message bot">
                <div class="message-content">
                    🤖 Bot đang suy nghĩ
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;

        // Insert after chat-messages container
        const messagesContainer = document.getElementById('chat-messages');
        if (messagesContainer && messagesContainer.parentNode) {
            messagesContainer.parentNode.insertBefore(indicator, messagesContainer.nextSibling);
        }

        console.log('🔄 Typing indicator recreated');
    }
    return indicator;
}

/**
 * Update status with better animations
 * @param {string} message - Status message
 * @param {string} type - Status type (ready, thinking, error)
 */
function updateStatus(message, type = 'ready') {
    const status = document.getElementById('status');
    if (!status) return;

    status.textContent = message;
    status.className = `status ${type}`;

    // Add pulse effect for important status changes
    if (type === 'error' || type === 'thinking') {
        status.style.animation = 'pulse 0.5s ease-in-out';
        setTimeout(() => {
            status.style.animation = '';
        }, 500);
    }
}

/**
 * Auto-resize textarea based on content
 */
function autoResizeTextarea() {
    const textarea = document.getElementById('message-input');
    if (textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
}

// ============================================================================
// ⌨️ INPUT HANDLING
// ============================================================================

/**
 * Handle Enter key press in input
 * @param {KeyboardEvent} event - The keyboard event
 */
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

/**
 * Handle before unload (optional cleanup)
 */
function handleBeforeUnload() {
    // Optional: Save draft or cleanup
    console.log('🔄 Page unloading...');
}

// ============================================================================
// 🛠️ CHAT MANAGEMENT FUNCTIONS
// ============================================================================

/**
 * Clear chat with improved cleanup and recreation
 */
async function clearChat() {
    // Show confirmation dialog
    if (!confirm('🗑️ Bạn có chắc chắn muốn xóa toàn bộ chat?')) {
        return;
    }

    try {
        // Call API to clear history
        const response = await fetch('/api/history/clear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();
        if (data.success) {
            // Hide typing indicator first to prevent errors
            showTyping(false);

            // Clear chat messages from UI
            const messagesContainer = document.getElementById('chat-messages');
            if (messagesContainer) {
                messagesContainer.innerHTML = `
                <div class="message system">
                    <div class="message-content">
                    🎉 <strong>Chào mừng bạn đến với BotQA!</strong><br><br>
                    💡 <strong>Bot sẽ tự động phát hiện và áp dụng template phù hợp:</strong><br>
                    • Thử: "Phân tích tình hình thị trường"<br>
                    • Thử: "Hướng dẫn cài đặt Python"<br>
                    • Thử: "Tóm tắt cuộc họp hôm nay"<br>
                    • Hoặc đặt câu hỏi bất kỳ!<br><br>
                    🎨 <strong>Click vào template bên trái để xem ví dụ</strong>
                    </div>
                </div>
                `;
            }

            updateStatus('🗑️ Đã xóa chat', 'ready');
        } else {
            updateStatus('❌ Không thể xóa chat', 'error');
        }
    } catch (error) {
        console.error('❌ Clear chat error:', error);
        updateStatus('❌ Lỗi khi xóa chat', 'error');
    }

    // Reset any ongoing processes
    isThinking = false;
    const sendBtn = document.getElementById('send-btn');
    if (sendBtn) {
        sendBtn.disabled = false;
        sendBtn.innerHTML = '📤 Gửi';
    }

    // Focus back to input
    const messageInput = document.getElementById('message-input');
    if (messageInput) {
        messageInput.focus();
    }

    console.log('🗑️ Chat cleared successfully');
}

/**
 * Save chat (copy to clipboard) with better feedback
 */
async function saveChat() {
    try {
        const messagesContainer = document.getElementById('chat-messages');
        if (!messagesContainer) return;

        const messages = messagesContainer.innerText;
        await navigator.clipboard.writeText(messages);

        updateStatus('💾 Đã copy chat vào clipboard!', 'ready');
        setTimeout(() => {
            updateStatus('✅ Sẵn sàng', 'ready');
        }, 2000);

        console.log('💾 Chat saved to clipboard');
    } catch (error) {
        console.error('❌ Save chat error:', error);
        updateStatus('❌ Không thể copy chat', 'error');
        setTimeout(() => {
            updateStatus('✅ Sẵn sàng', 'ready');
        }, 2000);
    }
}

/**
 * Export chat as JSON
 */
function exportChat() {
    window.open('/api/history/export', '_blank');
    updateStatus('📋 Đang xuất chat...', 'ready');
    setTimeout(() => {
        updateStatus('✅ Sẵn sàng', 'ready');
    }, 1000);
    console.log('📋 Chat export requested');
}

// ============================================================================
// 🚀 APPLICATION STARTUP
// ============================================================================

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeChat);
} else {
    initializeChat();
}

// Global error handling
window.addEventListener('error', function (event) {
    console.error('🚨 Global error:', event.error);
    updateStatus('❌ Có lỗi xảy ra', 'error');
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', function (event) {
    console.error('🚨 Unhandled promise rejection:', event.reason);
    updateStatus('❌ Lỗi hệ thống', 'error');
});

console.log('📦 BotQA Chat JavaScript loaded successfully!');
