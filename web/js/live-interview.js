// Live Interview Interface Module (Main Coordinator)
import { devLog, isDev } from './config.js';
import { LiveStreaming } from './live-streaming.js';
import { LiveControls } from './live-controls.js';
import muteManager from './mute-manager.js';

class LiveInterviewUI {
    constructor() {
        this.conversationStream = null;
        this.activityIndicator = null;
        this.endButton = null;
        this.muteButton = null;
        this.currentInterviewerElement = null; // Track interviewer message separately
        this.currentAIElement = null; // Track AI message separately
        this.isStreaming = false;
        this.eventsInitialized = false;
        
        // Enhanced smart scroll management
        this.scrollState = {
            mode: 'live_bottom',           // 'live_bottom', 'ai_start', 'user_override'
            userOverrideActive: false,     // Is user currently overriding scroll?
            userOverrideTimeout: null,     // Timeout to reset user override
            aiResponseStartElement: null,  // Reference to current AI response element
            isLiveSpeaking: false,         // Whether someone is currently speaking
            lastScrollPosition: 0,         // Track scroll position changes
            isNearBottom: true,            // Is the scroll position near the bottom?
        };
        
        // Initialize modules
        this.streaming = new LiveStreaming({
            enableStreaming: true,
            streamingSpeed: 15,
            aiStreamingSpeed: 5
        });
        
        this.controls = new LiveControls();
    }

    // Initialize elements
    init() {
        this.conversationStream = document.getElementById('conversation-stream');
        this.activityIndicator = document.getElementById('activity-indicator');
        this.endButton = document.getElementById('end-interview-btn');
        this.muteButton = document.getElementById('mute-btn');
        
        // Listen to the mute manager for state changes
        muteManager.on('stateChange', (status) => this.handleMuteStateChange(status));
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        if (this.eventsInitialized) return;

        if (this.endButton) {
            this.endButton.addEventListener('click', () => this.endInterview());
        }
        
        if (this.muteButton) {
            this.muteButton.addEventListener('click', () => this.toggleMute());
        }
        
        // Setup smart scroll detection
        this.setupSmartScroll();
        this.eventsInitialized = true;
    }

    setupSmartScroll() {
        if (!this.conversationStream) return;

        this.conversationStream.addEventListener('scroll', () => {
            const { scrollTop, scrollHeight, clientHeight } = this.conversationStream;
            this.scrollState.lastScrollPosition = scrollTop;
            this.scrollState.isNearBottom = scrollTop >= scrollHeight - clientHeight - 50; // 50px tolerance

            // If user scrolls up, activate override
            if (!this.scrollState.isNearBottom) {
                this.activateUserScrollOverride();
            } else {
                // If user scrolls back to bottom, deactivate override
                this.deactivateUserScrollOverride();
            }
        });

        // Also activate on wheel event for responsiveness
        this.conversationStream.addEventListener('wheel', (e) => {
            if (e.deltaY < 0) { // Scrolling up
                this.activateUserScrollOverride();
            }
        });
    }

    activateUserScrollOverride() {
        if (!this.scrollState.userOverrideActive) {
            this.scrollState.userOverrideActive = true;
            this.scrollState.mode = 'user_override';
            console.log('🖱️ User scroll override activated.');
        }

        // Reset the timeout each time the user scrolls
        clearTimeout(this.scrollState.userOverrideTimeout);
        this.scrollState.userOverrideTimeout = setTimeout(() => {
            this.scrollState.userOverrideActive = false;
            // Revert to a sensible default mode after timeout
            this.setScrollMode('live_bottom');
            console.log('🔄 User scroll override expired. Auto-scroll re-enabled.');
        }, 7000); // 3-second timeout
    }
    
    deactivateUserScrollOverride() {
        if (this.scrollState.userOverrideActive) {
            clearTimeout(this.scrollState.userOverrideTimeout);
            this.scrollState.userOverrideActive = false;
            this.setScrollMode('live_bottom');
            console.log('👍 User scrolled to bottom. Auto-scroll re-enabled.');
        }
    }

    // Show activity indicator
    showActivity(text = 'Listening...') {
        if (!this.activityIndicator) return;

        const status = muteManager.getMuteStatus();
        let indicatorText = text;
        
        if (status.universal) {
            indicatorText = '⏸️ System Paused - Press Alt+U to resume';
            this.activityIndicator.classList.add('paused');
        } else if (status.microphone) {
            indicatorText = '🔇 Microphone Muted - Press Alt+M to unmute';
            this.activityIndicator.classList.remove('paused');
        } else {
            this.activityIndicator.classList.remove('paused');
        }

        this.activityIndicator.querySelector('span').textContent = indicatorText;
        this.activityIndicator.classList.add('show');
    }

    hideActivity() {
        if (this.activityIndicator) {
            this.activityIndicator.classList.remove('show');
        }
    }

    // Add interviewer question
    addInterviewerQuestion(question, isInterim = false) {
        this.setScrollMode('live_bottom'); // Always scroll to bottom for live speech
        this.scrollState.isLiveSpeaking = true;

        if (isInterim) {
            if (!this.currentInterviewerElement) {
                this.currentInterviewerElement = this.createMessageElement('', 'interviewer');
                this.conversationStream.appendChild(this.currentInterviewerElement);
                this.updateEmptyState();
            }
            this.updateInterviewerMessage(this.currentInterviewerElement.querySelector('.streaming-text').textContent + ' ' + question);
        } else {
            if (this.currentInterviewerElement) {
                this.finalizeInterviewerMessage(question);
            } else {
                this.addMessage(question, 'interviewer');
            }
            this.hideActivity();
            this.updateEmptyState();
            this.scrollState.isLiveSpeaking = false;
        }
        this.scrollToBottom(); // Continuous scroll during speech
    }

    // Add AI response
    addAIResponse(response) {
        this.currentAIElement = this.createMessageElement(response, 'ai-response');
        this.conversationStream.appendChild(this.currentAIElement);

        this.setScrollMode('ai_start', this.currentAIElement);

        this.startStreaming(this.currentAIElement, response, true, () => {
            // On completion, set mode back to ready for live speech
            this.setScrollMode('live_bottom');
        });
        
        this.hideActivity();
        this.updateEmptyState();
    }

    // Add message to conversation
    addMessage(content, type) {
        const messageElement = this.createMessageElement(content, type);
        this.conversationStream.appendChild(messageElement);
        this.startStreaming(messageElement, content);
        this.scrollToBottom();
        this.updateEmptyState();
    }

    // Create message element
    createMessageElement(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const label = document.createElement('span');
        label.className = 'label';
        label.textContent = type === 'interviewer' ? '🎤 Interviewer' : '🤖 AI Assistant';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'streaming-text';
        
        messageDiv.appendChild(label);
        messageDiv.appendChild(contentDiv);
        
        return messageDiv;
    }

    // Start streaming animation (delegated to streaming module)
    startStreaming(messageElement, content, isAI = false, onCompletion = null) {
        const contentDiv = messageElement.querySelector('.streaming-text');
        const speed = isAI ? this.streaming.config.aiStreamingSpeed : this.streaming.config.streamingSpeed;

        this.isStreaming = true;

        const scrollCallback = () => {
            // Only auto-scroll during live speech streaming
            if (this.scrollState.mode === 'live_bottom') {
                this.scrollToBottom();
            }
        };

        this.streaming.streamContent(contentDiv, content, speed, scrollCallback).then(() => {
            messageElement.classList.add('complete');
            this.isStreaming = false;
            if (onCompletion) {
                onCompletion();
            }
        });
    }

    // Update interviewer message (for interim results)
    updateInterviewerMessage(content) {
        if (this.currentInterviewerElement) {
            const contentDiv = this.currentInterviewerElement.querySelector('.streaming-text');
            
            // Mark as interim to hide typing cursor
            this.currentInterviewerElement.classList.add('interim');
            
            // Clear and update instantly using streaming module
            contentDiv.innerHTML = '';
            this.streaming.displayInstantText(contentDiv, content);
        }
    }

    // Finalize interviewer message (for final results)
    finalizeInterviewerMessage(content) {
        if (this.currentInterviewerElement) {
            // Remove interim class to show typing animation for final result
            this.currentInterviewerElement.classList.remove('interim');
            
            const contentDiv = this.currentInterviewerElement.querySelector('.streaming-text');
            contentDiv.innerHTML = '';
            
            // Use streaming module for final content
            this.streaming.streamContent(contentDiv, content, this.streaming.config.streamingSpeed).then(() => {
                if (this.currentInterviewerElement) {
                    this.currentInterviewerElement.classList.add('complete');
                }
            });
            
            // Clear the reference since this is final
            this.currentInterviewerElement = null;
            
            // Reset auto-scroll for new response
            this.autoScrollEnabled = true;
        }
    }

    // --- New Smart Scrolling System ---

    setScrollMode(mode, targetElement = null) {
        this.scrollState.mode = mode;
        devLog(`📜 Scroll mode set to: ${mode}`);

        switch (mode) {
            case 'live_bottom':
                this.scrollToBottom();
                break;
            case 'ai_start':
                if (targetElement) {
                    this.scrollState.aiResponseStartElement = targetElement;
                    this.scrollToAiResponseStart();
                }
                break;
            case 'user_override':
                // In this mode, we don't trigger any automatic scrolling
                break;
        }
    }

    scrollToBottom() {
        if (this.scrollState.userOverrideActive) {
            // console.log('📜 Scroll to bottom blocked by user override.');
            return;
        }
        if (this.conversationStream) {
            this.conversationStream.scrollTop = this.conversationStream.scrollHeight;
        }
    }

    scrollToAiResponseStart() {
        if (this.scrollState.userOverrideActive) {
            // console.log('📜 Scroll to AI response start blocked by user override.');
            return;
        }
        if (this.scrollState.aiResponseStartElement) {
            this.scrollState.aiResponseStartElement.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }

    // Clear conversation
    clearConversation() {
        if (this.conversationStream) {
            this.conversationStream.innerHTML = '';
        }
        this.currentInterviewerElement = null;
        this.currentAIElement = null;
        this.isStreaming = false;
        this.updateEmptyState();
    }

    // Update empty state class
    updateEmptyState() {
        if (!this.conversationStream) return;
        
        const messageCount = this.conversationStream.querySelectorAll('.message').length;
        if (messageCount === 0) {
            this.conversationStream.classList.add('no-messages');
        } else {
            this.conversationStream.classList.remove('no-messages');
        }
    }

    // Toggle microphone mute via the UI button
    toggleMute() {
        // The hotkey manager and mute manager now handle the logic.
        // This just needs to trigger the toggle.
        muteManager.toggleMicrophoneMute();
    }

    // Central handler for all mute state changes
    handleMuteStateChange(status) {
        this.updateMuteButton(status.microphone);
        this.showActivity(); // Re-evaluates the activity indicator text
        devLog(`UI updated for mute state: Mic=${status.microphone}, Universal=${status.universal}`);
    }

    // Update mute button appearance
    updateMuteButton(isMuted) {
        if (this.muteButton) {
            if (isMuted) {
                this.muteButton.classList.add('muted');
                this.muteButton.title = 'Unmute microphone input to app (Alt+M)';
            } else {
                this.muteButton.classList.remove('muted');
                this.muteButton.title = 'Mute microphone input to app (Alt+M)';
            }
        }
    }

    // End interview
    endInterview() {
        if (typeof window.endInterview === 'function') {
            window.endInterview();
        }
    }

    // Initialize
    initialize() {
        this.clearConversation();
        this.showActivity('Listening...');
        this.controls.initialize(); // Initialize controls module
        this.updateEmptyState();
        
        // Set initial UI state from the mute manager
        const initialStatus = muteManager.getMuteStatus();
        this.updateMuteButton(initialStatus.microphone);
        console.log(`🎤 UI initialized with microphone ${initialStatus.microphone ? 'muted' : 'unmuted'}`);
        
        // Reset scroll state
        this.scrollState = {
            mode: 'live_bottom',
            userOverrideActive: false,
            userOverrideTimeout: null,
            aiResponseStartElement: null,
            isLiveSpeaking: false,
            lastScrollPosition: 0,
            isNearBottom: true,
        };
        
        console.log('🎬 Live interview UI initialized');
    }

    // Get current configuration
    getConfig() {
        return {
            streaming: this.streaming.getConfig(),
            transparency: this.controls.getConfig()
        };
    }
}

// Create global instance
window.liveInterviewUI = new LiveInterviewUI();

// Add global configuration functions for easy control
window.setInterviewStreaming = (enabled) => {
    window.liveInterviewUI.streaming.setStreamingEnabled(enabled);
    console.log(`🎬 Streaming ${enabled ? 'enabled' : 'disabled'}`);
};

window.setInterviewSpeed = (speed) => {
    window.liveInterviewUI.streaming.setStreamingSpeed(speed);
    console.log(`⚡ Interviewer streaming speed set to ${speed}ms`);
};

window.setAISpeed = (speed) => {
    window.liveInterviewUI.streaming.setAIStreamingSpeed(speed);
    console.log(`🤖 AI streaming speed set to ${speed}ms`);
};

window.setMarkdownEnabled = (enabled) => {
    window.liveInterviewUI.streaming.setMarkdownEnabled(enabled);
    console.log(`📝 Markdown processing ${enabled ? 'enabled' : 'disabled'}`);
};

window.setMarkdownSpeed = (speed) => {
    window.liveInterviewUI.streaming.setMarkdownSpeed(speed);
    console.log(`📝 Markdown element speed set to ${speed}ms`);
};

// Process All Speakers Configuration
window.setProcessAllSpeakers = (enabled) => {
    // This function will be fully implemented in main.js where the socket is managed
    if (typeof window.sendSocketMessage === 'function') {
        window.sendSocketMessage('config_update', {
            processAllSpeakers: enabled
        });
        console.log(`🎯 Process All Speakers config sent: ${enabled}`);
    } else {
        console.warn('sendSocketMessage not defined yet. Make sure it is globally available.');
    }
};

window.enableAllSpeakers = () => {
    window.setProcessAllSpeakers(true);
    console.log('🎯 All speakers mode activated - AI will respond to everyone');
};

window.disableAllSpeakers = () => {
    window.setProcessAllSpeakers(false);
    console.log('🎯 Interviewer-only mode activated - AI will only respond to interviewer');
};

// Smart scroll controls
window.setScrollMode = (mode) => {
    if (window.liveInterviewUI) {
        window.liveInterviewUI.setScrollMode(mode);
    }
};

window.getScrollState = () => {
    if (window.liveInterviewUI) {
        return window.liveInterviewUI.scrollState;
    }
    return null;
};

// Quick presets
window.setFastStreaming = () => {
    window.setInterviewSpeed(15);
    window.setAISpeed(8);
    console.log('🚀 Fast streaming mode activated');
};

window.setSlowStreaming = () => {
    window.setInterviewSpeed(50);
    window.setAISpeed(30);
    console.log('🐌 Slow streaming mode activated');
};

window.setInstantMode = () => {
    window.setInterviewStreaming(false);
    console.log('⚡ Instant mode activated - no streaming animations');
};

// Markdown-specific presets
window.setFastMarkdown = () => {
    window.setMarkdownEnabled(true);
    window.setMarkdownSpeed(50);
    window.setInterviewSpeed(8);
    window.setAISpeed(3);
    console.log('📝 Fast markdown mode activated');
};

window.setSlowMarkdown = () => {
    window.setMarkdownEnabled(true);
    window.setMarkdownSpeed(150);
    window.setInterviewSpeed(20);
    window.setAISpeed(6);
    console.log('📝 Slow markdown mode activated');
};

window.disableMarkdown = () => {
    window.setMarkdownEnabled(false);
    console.log('📝 Markdown processing disabled - plain text only');
};

window.enableMarkdown = () => {
    window.setMarkdownEnabled(true);
    console.log('📝 Markdown processing enabled - formatted text');
};

export default window.liveInterviewUI; 