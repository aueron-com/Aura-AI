// Hotkeys Module for Aura
// Provides keyboard shortcuts for transparency and other controls

import { devLog } from './config.js';

class HotkeyManager {
    constructor() {
        this.isAltLPressed = false;
        this.transparencyLevels = [0.2, 0.4, 0.6, 0.8, 1.0]; // 5 levels: 20%, 40%, 60%, 80%, 100%
        this.currentTransparencyLevel = 3; // Default to 80% (index 3)
        this.isEnabled = true;
        this.isAlwaysOnTop = true; // Track always-on-top state
        
        this.setupEventListeners();
        devLog('🎹 Hotkey manager initialized');
    }

    setupEventListeners() {
        document.addEventListener('keydown', this.handleKeyDown.bind(this));
        document.addEventListener('keyup', this.handleKeyUp.bind(this));
        
        // Prevent default browser shortcuts that might interfere
        document.addEventListener('keydown', (e) => {
            if (e.altKey && (e.key.toLowerCase() === 'l' || e.key.toLowerCase() === 'm')) {
                e.preventDefault();
            }
        });
    }

    handleKeyDown(event) {
        if (!this.isEnabled) return;

        // Check for Alt+M combination (microphone mute)
        if (event.altKey && event.key.toLowerCase() === 'm') {
            this.toggleMicrophoneMute();
            event.preventDefault();
            return;
        }

        // Check for Alt+L combination
        if (event.altKey && event.key.toLowerCase() === 'l') {
            this.isAltLPressed = true;
            this.showTransparencyHint();
            event.preventDefault();
            return;
        }

        // Handle transparency controls when Alt+L is held
        if (this.isAltLPressed) {
            switch (event.key) {
                case '[':
                    this.decreaseTransparency();
                    event.preventDefault();
                    break;
                case ']':
                    this.increaseTransparency();
                    event.preventDefault();
                    break;
                case 'Escape':
                    this.hideTransparencyHint();
                    break;
                case 't':
            }
        }
    }

    handleKeyUp(event) {
        if (event.key === 'Alt' || event.key.toLowerCase() === 'l') {
            this.isAltLPressed = false;
            this.hideTransparencyHint();
        }
    }

    decreaseTransparency() {
        if (this.currentTransparencyLevel > 0) {
            this.currentTransparencyLevel--;
            this.applyTransparency();
        }
    }

    increaseTransparency() {
        if (this.currentTransparencyLevel < this.transparencyLevels.length - 1) {
            this.currentTransparencyLevel++;
            this.applyTransparency();
        }
    }

    async applyTransparency() {
        const transparency = this.transparencyLevels[this.currentTransparencyLevel];
        const percent = Math.round(transparency * 100);
        
        try {
            // Only allow transparency changes during live interview
            const currentView = document.querySelector('.view.active');
            const isLiveView = currentView && currentView.id === 'live-view';
            
            if (!isLiveView) {
                console.log('ℹ️ Transparency hotkeys only work during live interview');
                this.showTransparencyFeedback(100, 'Transparency only available in live interview');
                return;
            }
            
            // Apply Windows-level transparency
            const response = await fetch('/api/transparency', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ transparency: transparency })
            });
            
            if (response.ok) {
                devLog(`🪟 Transparency set to ${percent}% via hotkey`);
                this.showTransparencyFeedback(percent);
            }
        } catch (error) {
            console.error('❌ Error setting transparency via hotkey:', error);
        }
    }

    showTransparencyHint() {
        this.removeExistingHints();
        
        const hint = document.createElement('div');
        hint.id = 'transparency-hint';
        hint.innerHTML = `
            <div class="hotkey-hint">
                <div class="hint-title">🎹 Transparency Control</div>
                <div class="hint-controls">
                    <span class="hint-key">Alt+L + [</span> Less Transparent
                    <span class="hint-key">Alt+L + ]</span> More Transparent
                    <span class="hint-key">Alt+M</span> Toggle Microphone Mute
                </div>
                <div class="hint-level">Level: ${this.currentTransparencyLevel + 1}/5 (${Math.round(this.transparencyLevels[this.currentTransparencyLevel] * 100)}%)</div>
            </div>
        `;
        
        document.body.appendChild(hint);
    }

    hideTransparencyHint() {
        const hint = document.getElementById('transparency-hint');
        if (hint) {
            hint.remove();
        }
    }

    showTransparencyFeedback(percent, message = null) {
        this.removeExistingFeedback();
        
        const feedback = document.createElement('div');
        feedback.id = 'transparency-feedback';
        
        if (message) {
            feedback.innerHTML = `
                <div class="transparency-feedback">
                    ℹ️ ${message}
                </div>
            `;
        } else {
            feedback.innerHTML = `
                <div class="transparency-feedback">
                    🪟 ${percent}% Opacity
                    <div class="transparency-bar">
                        ${this.generateTransparencyBar()}
                    </div>
                </div>
            `;
        }
        
        document.body.appendChild(feedback);
        
        // Auto-hide after 2 seconds
        setTimeout(() => {
            if (feedback.parentNode) {
                feedback.remove();
            }
        }, 2000);
    }

    generateTransparencyBar() {
        let bar = '';
        for (let i = 0; i < this.transparencyLevels.length; i++) {
            const isActive = i === this.currentTransparencyLevel;
            bar += `<span class="bar-segment ${isActive ? 'active' : ''}">${isActive ? '●' : '○'}</span>`;
        }
        return bar;
    }

    removeExistingHints() {
        const existing = document.getElementById('transparency-hint');
        if (existing) existing.remove();
    }

    removeExistingFeedback() {
        const existing = document.getElementById('transparency-feedback');
        if (existing) existing.remove();
    }

    // Public methods for external control
    setEnabled(enabled) {
        this.isEnabled = enabled;
        devLog(`🎹 Hotkeys ${enabled ? 'enabled' : 'disabled'}`);
    }

    getCurrentTransparency() {
        return {
            level: this.currentTransparencyLevel + 1,
            percent: Math.round(this.transparencyLevels[this.currentTransparencyLevel] * 100),
            value: this.transparencyLevels[this.currentTransparencyLevel]
        };
    }

    setTransparencyLevel(level) {
        if (level >= 1 && level <= 5) {
            this.currentTransparencyLevel = level - 1;
            this.applyTransparency();
        }
    }


    toggleMicrophoneMute() {
        // Only allow mute toggle during live interview
        const currentView = document.querySelector('.view.active');
        const isLiveView = currentView && currentView.id === 'live-view';
        
        if (!isLiveView) {
            console.log('ℹ️ Microphone mute only available during live interview');
            this.showMuteFeedback(false, 'Microphone mute only available in live interview');
            return;
        }

        if (typeof window.toggleMicrophoneMute === 'function') {
            const isMuted = window.toggleMicrophoneMute();
            this.showMuteFeedback(isMuted);
            
            // Update the mute button if it exists
            if (window.liveInterviewUI && window.liveInterviewUI.updateMuteButton) {
                window.liveInterviewUI.updateMuteButton(isMuted);
                
                // Update activity indicator text based on mute state
                if (window.liveInterviewUI.activityIndicator && 
                    window.liveInterviewUI.activityIndicator.classList.contains('show')) {
                    window.liveInterviewUI.showActivity();
                }
            }
            
            devLog(`🎤 Microphone ${isMuted ? 'muted' : 'unmuted'} via hotkey`);
        }
    }

    showMuteFeedback(isMuted, message = null) {
        this.removeExistingFeedback();
        
        const feedback = document.createElement('div');
        feedback.id = 'transparency-feedback';
        
        if (message) {
            feedback.innerHTML = `
                <div class="transparency-feedback">
                    ℹ️ ${message}
                </div>
            `;
        } else {
            feedback.innerHTML = `
                <div class="transparency-feedback">
                    🎤 Microphone ${isMuted ? 'Muted' : 'Unmuted'}
                    <div class="mute-status">${isMuted ? '🔇 App audio input disabled' : '🎙️ App audio input enabled'}</div>
                </div>
            `;
        }
        
        document.body.appendChild(feedback);
        
        // Auto-hide after 2 seconds
        setTimeout(() => {
            if (feedback.parentNode) {
                feedback.remove();
            }
        }, 2000);
    }
}

// Create global instance
const hotkeyManager = new HotkeyManager();

// Global functions for console access
window.enableHotkeys = () => hotkeyManager.setEnabled(true);
window.disableHotkeys = () => hotkeyManager.setEnabled(false);
window.getTransparencyLevel = () => hotkeyManager.getCurrentTransparency();
window.setTransparencyLevel = (level) => hotkeyManager.setTransparencyLevel(level);

export default hotkeyManager; 