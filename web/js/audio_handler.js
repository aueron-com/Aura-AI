// --- audio_handler.js ---
// This module handles all interactions with the Web Media APIs
// for capturing and processing audio via an AudioWorklet.

import { devLog, devError } from './config.js';
import muteManager from './mute-manager.js';

let audioContext = null;
let micStream = null;
let systemStream = null;
let micGainNode = null;
let screenVideoTrack = null; // Store video track for screenshot reuse

/**
 * Requests permission to use the microphone and populates the dropdown.
 * @returns {Promise<boolean>} True if permission was granted, false otherwise.
 */
export async function setupMicrophone() {
    const micSelect = document.getElementById('mic-select');
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
        stream.getTracks().forEach(track => track.stop());

        const devices = await navigator.mediaDevices.enumerateDevices();
        const audioDevices = devices.filter(device => device.kind === 'audioinput');

        if (audioDevices.length === 0) return false;

        micSelect.innerHTML = '';
        audioDevices.forEach(device => {
            const option = document.createElement('option');
            option.value = device.deviceId;
            option.textContent = device.label || `Microphone ${micSelect.options.length + 1}`;
            micSelect.appendChild(option);
        });
        
        micSelect.disabled = false;
        return true;
    } catch (err) {
        devError("Error setting up microphone:", err);
        return false;
    }
}

/**
 * Starts audio processing by setting up the AudioContext, loading the worklet,
 * and connecting the audio streams.
 * @param {string|null} micId - The deviceId of the selected microphone. Ignored when opts.interviewerOnly is true.
 * @param {function} onAudioData - Callback function to handle the processed PCM audio data.
 * @param {{ interviewerOnly?: boolean }} [opts] - Optional flags. When interviewerOnly is true,
 *   the candidate microphone is not requested or captured; only the shared tab/system audio
 *   from getDisplayMedia is fed to the worklet and every chunk is tagged speakerHint='system'.
 * @returns {Promise<boolean>} True if processing started successfully.
 */
export async function startAudioProcessing(micId, onAudioData, opts = {}) {
    const interviewerOnly = !!opts.interviewerOnly;
    try {
        // 1. Get Audio Streams
        if (!interviewerOnly) {
            micStream = await navigator.mediaDevices.getUserMedia({ audio: { deviceId: { exact: micId } } });
        }
        systemStream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: true });

        // Fail early if the required streams are missing.
        if (!systemStream) {
            console.error("Could not get system/tab audio stream.");
            stopAudioProcessing();
            return false;
        }
        if (!interviewerOnly && !micStream) {
            console.error("Could not get microphone stream.");
            stopAudioProcessing();
            return false;
        }
        // In interviewer-only mode the shared audio track is the ONLY signal —
        // if the user forgot to check "Share tab/system audio", refuse to start.
        if (interviewerOnly && systemStream.getAudioTracks().length === 0) {
            console.error("Interviewer-only mode requires shared tab/system audio, but no audio track was granted.");
            stopAudioProcessing();
            return false;
        }

        // 2. Setup AudioContext and Worklet
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        console.log(`🎵 AudioContext: ${audioContext.sampleRate}Hz`); // Keep this as it's important for debugging
        await audioContext.audioWorklet.addModule('/static/js/audio_processor.js');

        // 3. Create the processor. In interviewer-only mode the worklet skips
        // mixing math and passes the single system input through at full amplitude.
        const mixedProcessor = new AudioWorkletNode(audioContext, 'mixed-processor', {
            processorOptions: { interviewerOnly }
        });

        // Handle mixed audio with mute-aware speaker detection
        let audioProcessingCounter = 0; // For throttled logging

        mixedProcessor.port.onmessage = (event) => {
            // If universally muted, drop all audio data immediately.
            if (muteManager.isAudioPaused()) {
                if (audioProcessingCounter % 200 === 0) { // Log occasionally to show it's paused
                    devLog(`⏸️ Audio processing paused due to universal mute.`);
                }
                audioProcessingCounter++;
                return;
            }

            const { audioData, micLevel, systemLevel } = event.data;
            let speakerHint;

            if (interviewerOnly) {
                // No candidate audio path exists — every chunk is the interviewer.
                speakerHint = 'system';
            } else if (muteManager.isMicrophoneMuted()) {
                // When microphone is muted, all audio is from the interviewer.
                speakerHint = 'system';
            } else {
                // When unmuted, distinguish based on volume.
                speakerHint = systemLevel > micLevel * 2 ? 'system' : 'microphone';
            }

            audioProcessingCounter++;
            onAudioData(audioData, speakerHint);
        };

        // 4. Wire audio sources into the processor.
        const systemSource = audioContext.createMediaStreamSource(systemStream);

        if (!interviewerOnly) {
            const micSource = audioContext.createMediaStreamSource(micStream);
            // Gain node lets us mute the mic without tearing down the graph.
            micGainNode = audioContext.createGain();
            updateMicGainNode(); // Set initial gain based on mute manager state
            muteManager.on('microphoneMuteChange', updateMicGainNode);

            micSource.connect(micGainNode);
            micGainNode.connect(mixedProcessor);
        }

        // System audio always connects directly (we don't want to mute interviewer).
        // In interviewer-only mode this is input[0] on the worklet since no mic is wired.
        systemSource.connect(mixedProcessor);

        // Store the video track for screenshot reuse, but remove it from the stream
        const videoTracks = systemStream.getVideoTracks();
        if (videoTracks.length > 0) {
            screenVideoTrack = videoTracks[0];
            console.log("📹 Screen video track stored for screenshot reuse");
        } else {
            console.warn("⚠️ No video track found in display media stream");
        }

        devLog(`✅ Audio processing started successfully${interviewerOnly ? ' (interviewer-only mode)' : ''}`);
        return true;

    } catch (err) {
        console.error("❌ Error starting audio processing:", err);
        stopAudioProcessing();
        return false;
    }
}

/**
 * Updates the microphone gain node based on the central mute manager state.
 */
function updateMicGainNode() {
    if (!micGainNode || !audioContext) return;
    
    const isMuted = muteManager.isMicrophoneMuted();
    const targetGain = isMuted ? 0 : 1;
    
    // Smooth transition to avoid audio pops
    micGainNode.gain.setTargetAtTime(targetGain, audioContext.currentTime, 0.05);
    devLog(`🎤 Microphone gain set to ${targetGain} based on mute manager.`);
}

// --- Legacy Functions (now wrappers for MuteManager) ---
// These are kept for backward compatibility with other modules that might call them.

/**
 * @deprecated Use muteManager.setMicrophoneMute(mute) instead.
 */
export function setMicrophoneMute(mute) {
    muteManager.setMicrophoneMute(mute);
    return muteManager.isMicrophoneMuted();
}

/**
 * @deprecated Use muteManager.isMicrophoneMuted() instead.
 */
export function isMicrophoneMuted() {
    return muteManager.isMicrophoneMuted();
}

/**
 * @deprecated Use muteManager.toggleMicrophoneMute() instead.
 */
export function toggleMicrophoneMute() {
    return muteManager.toggleMicrophoneMute();
}

/**
 * @deprecated Use muteManager.getMuteStatus() instead.
 */
export function getAudioProcessingMode() {
    return muteManager.getMuteStatus();
}

/**
 * Gets the screen video track for screenshot capture.
 * @returns {MediaStreamTrack|null} The screen video track if available.
 */
export function getScreenVideoTrack() {
    return screenVideoTrack;
}

/**
 * Checks if screen sharing is available for screenshots.
 * @returns {boolean} True if screen video track is available and active.
 */
export function isScreenSharingAvailable() {
    return screenVideoTrack && screenVideoTrack.readyState === 'live';
}

/**
 * Stops all audio streams and closes the AudioContext.
 */
export function stopAudioProcessing() {
    console.log("Stopping audio processing.");
    if (micStream) {
        micStream.getTracks().forEach(track => track.stop());
        micStream = null;
    }
    if (systemStream) {
        systemStream.getTracks().forEach(track => track.stop());
        systemStream = null;
    }
    if (screenVideoTrack) {
        screenVideoTrack.stop();
        screenVideoTrack = null;
        console.log("📹 Screen video track stopped");
    }
    if (audioContext && audioContext.state !== 'closed') {
        audioContext.close();
        audioContext = null;
    }
    
    // Reset mute state in the central manager
    muteManager.setMicrophoneMute(true);
    muteManager.setUniversalMute(false);
    micGainNode = null;
}