# Smart Auto-Scrolling System Implementation Plan

## Overview
Implementation of a context-aware auto-scrolling system for the live interview chat interface that provides:
- Live speech auto-scrolling to bottom
- AI response start scrolling 
- User override handling with contextual re-enabling
- Smooth transitions between scroll modes

## Current State Analysis

### Existing Implementation
- Basic scroll detection in `live-interview.js` lines 63-126
- Simple timeout-based re-enabling (5 seconds) - from users latest scroll activity
- `scrollToBottom()` method with user interaction respect
- Variables: `userHasScrolled`, `autoScrollEnabled`, `scrollTimeout`

### Issues to Address
- No distinction between live speech and AI response contexts
- No mechanism to scroll to AI response start
- Non-contextual timeout-based re-enabling
- Missing integration with speech state changes

## Implementation Plan

### Phase 1: Enhanced Scroll State Management

#### New State Object
Replace current scroll variables with comprehensive state management:

```javascript
this.scrollState = {
    mode: 'live_bottom',           // 'live_bottom', 'ai_start', 'user_override'
    userOverrideTime: null,        // When user last scrolled manually
    aiResponseStartElement: null,  // Reference to current AI response element
    isLiveSpeaking: false,         // Whether someone is currently speaking
    lastScrollPosition: 0,         // Track scroll position changes
    continuousScrolling: false     // Flag for continuous scroll loop
}
```

#### Core Methods to Implement

1. **`enableLiveSpeechScrolling()`** - Activate continuous bottom scrolling
2. **`scrollToAIResponseStart(aiElement)`** - Scroll to AI response beginning
3. **`detectUserScrollOverride()`** - Enhanced user interaction detection
4. **`isUserOverrideActive()`** - Context-aware override checking
5. **`scheduleScrollReEnable()`** - Smart re-enabling based on context
6. **`continuousScrollToBottom()`** - Smooth continuous scrolling during speech

### Phase 2: Integration Points

#### A) Live Speech Integration
**Target: `addInterviewerQuestion()` method**
- Enable live speech scrolling for interim results
- Maintain continuous bottom scrolling during transcription
- Override user scroll during active speech (with shorter timeout)

#### B) AI Response Integration  
**Target: `addAIResponse()` method**
- Scroll to AI response start when response begins
- Store reference to AI response element
- Switch to live-ready mode when AI response completes

#### C) Activity State Integration
**Target: `showActivity()` and `hideActivity()` methods**
- Link scroll modes to listening/processing states
- Coordinate with speech detection

### Phase 3: Enhanced User Override Logic

#### Improved Detection
- Scroll position monitoring with tolerance zones
- Context-aware timeout values (2s during speech, 5s idle)
- Immediate override on intentional scroll-up gestures

#### Smart Re-enabling
- Shorter timeouts during active speech
- Automatic mode switching based on activity state
- Progressive timeout scaling

### Phase 4: Streaming Integration

#### Streaming Callback Enhancement
**Target: `startStreaming()` method**
- Context-aware scroll callbacks during streaming
- Mode transitions based on content type
- Smooth scroll coordination with typing animation

### Phase 5: Configuration & Controls

#### Configuration Options
```javascript
scrollConfig: {
    liveScrollEnabled: true,
    aiStartScrollEnabled: true,
    userOverrideTimeout: 3000,
    speechOverrideTimeout: 2000,
    scrollTolerance: 50,
    smoothScrolling: true
}
```

#### Global Control Functions
- `enableSmartScrolling()` / `disableSmartScrolling()`
- `forceScrollMode(mode)` for debugging
- `getScrollState()` for status checking

## Implementation Details

### Scroll State Flow

```
Initialize → LiveBottom
LiveBottom → LiveSpeaking (speech starts)
LiveSpeaking → UserOverride (user scrolls)
LiveBottom → AIStart (AI response begins)
AIStart → LiveBottom (AI response complete)
UserOverride → [context-dependent] (timeout/activity)
```

### Key Behavioral Changes

1. **During Live Speech**
   - Continuous auto-scroll to bottom
   - Shorter user override timeout (2s)
   - Force scroll even during user interaction (unless recent manual scroll)

2. **AI Response Start**
   - Smooth scroll to beginning of AI response
   - Mark AI response element for reference
   - Disable continuous scrolling during AI response

3. **User Override**
   - Respect manual scrolling immediately
   - Context-aware re-enabling timeouts
   - Visual feedback (optional)

### Technical Implementation

#### Modified Methods
- `setupSmartScroll()` - Replace existing `setupSmartScroll()`
- `addInterviewerQuestion()` - Add live speech scroll mode
- `addAIResponse()` - Add AI start scroll functionality
- `startStreaming()` - Enhanced scroll coordination
- `showActivity()` / `hideActivity()` - State coordination

#### New Methods
- `enableLiveSpeechScrolling()`
- `scrollToAIResponseStart()`
- `continuousScrollToBottom()`
- `detectUserScrollOverride()`
- `isUserOverrideActive()`
- `scheduleScrollReEnable()`

#### Utility Methods
- `getCurrentScrollMode()`
- `setScrollMode(mode)`
- `resetScrollState()`

## Testing Scenarios

1. **Live Speech Flow**
   - Start speaking → auto-scroll to bottom
   - User scrolls up during speech → temporary override
   - Resume speaking → auto-scroll resumes after timeout

2. **AI Response Flow**
   - AI starts responding → scroll to AI response start
   - AI completes → ready for next live speech
   - User scrolls during AI response → override respected

3. **Mixed Scenarios**
   - Rapid speech-to-AI transitions
   - Multiple user scroll interruptions
   - Long AI responses with user interaction

## Success Criteria

- ✅ Live speech always auto-scrolls to bottom
- ✅ AI responses start scrolling from response beginning
- ✅ User manual scrolling is respected immediately
- ✅ Context-aware re-enabling based on activity
- ✅ Smooth transitions between scroll modes
- ✅ No jarring scroll jumps or conflicts
- ✅ Maintains performance during long conversations

## Files to Modify

1. **`web/js/live-interview.js`** - Primary implementation
   - Replace scroll state management
   - Enhance integration methods
   - Add new scroll mode methods

2. **Global Functions** - Add configuration controls
   - Smart scrolling toggle functions
   - Debug and status functions

## Configuration Options

Users will be able to control:
- Enable/disable smart scrolling
- Adjust timeout values
- Configure scroll tolerance
- Toggle smooth scrolling behavior