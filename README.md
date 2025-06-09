# 🌟 Aura AI Interview Coach

**The Ultimate AI-Powered Interview Assistant with Vision, Voice, and Advanced Coaching**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)
[![WebSockets](https://img.shields.io/badge/WebSockets-Real--time-orange.svg)](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
[![AI Vision](https://img.shields.io/badge/AI-Vision%20Enabled-purple.svg)](https://openai.com/research/gpt-4v-system-card)

> 🚀 **Revolutionary interview preparation with real-time AI assistance, screenshot analysis, and comprehensive coaching across coding, system design, and behavioral questions.**

---

## 📖 Table of Contents

- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [⚙️ Installation](#️-installation)
- [🎮 Global Hotkeys](#-global-hotkeys)
- [👁️ Vision AI Capabilities](#️-vision-ai-capabilities)
- [🗄️ SQL Support](#️-sql-support)
- [🎯 Usage Guide](#-usage-guide)
- [🔧 Configuration](#-configuration)
- [🏗️ Architecture](#️-architecture)
- [📚 API Documentation](#-api-documentation)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## ✨ Features

### 🎤 **Real-Time Voice Processing**
- **Live transcription** with Deepgram AI
- **Smart audio processing** with configurable mute controls
- **Universal pause system** for complete audio control

### 🤖 **Multi-LLM AI Support**
- **Primary & Secondary Models** with instant switching
- **Auto-failover** to backup providers for reliability
- **Health monitoring** and intelligent provider selection
- **Supported Providers**: Groq, Cerebras, Gemini, and more

### 👁️ **Advanced Vision AI**
- **Screenshot analysis** of coding problems, databases, and diagrams
- **Multi-screenshot processing** for complex problems
- **Smart content detection** (code vs database vs system design)
- **Language-specific solutions** in Python, Java, JavaScript, C++, SQL, and more

### 🎮 **System-Wide Global Hotkeys**
- **Universal control** from any application
- **Vision mode** for screenshot capture and analysis
- **AI model switching** without disrupting workflow
- **Transparency controls** for interview overlay
- **Audio controls** for microphone and system muting

### 🧠 **Intelligent Context Management**
- **Persistent candidate profile** with unlimited resume and job description storage
- **Conversation history** tracking up to 6+ exchanges
- **Cross-reference capabilities** - ask about previous questions anytime
- **No token truncation** - full context preserved

### 🔒 **Stealth & Privacy**
- **Screen capture protection** - appears as black rectangle in recordings
- **Taskbar hiding** for complete discretion
- **Always on top** window management
- **Ghost mode** for click-through functionality

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Windows 10/11 (for advanced features)
- Microphone access
- AI API keys (Groq/Cerebras/Gemini)
- Deepgram API key

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/aura-ai-interview-coach.git
cd aura-ai-interview-coach

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the application
python main.py
```

### First Launch
1. **Configure API Keys** in `.env` file
2. **Complete Onboarding** - Add your profile, resume, and target role
3. **Setup AI Models** - Select primary and secondary providers
4. **Enable Vision AI** (optional) - Choose vision model for screenshot analysis
5. **Start Interview** - Begin your AI-assisted interview session

---

## 🎮 Global Hotkeys

> **Note**: These hotkeys work system-wide from any application!

### 🪟 **Window Controls**
| Hotkey | Function | Description |
|--------|----------|-------------|
| `Alt + X` | Toggle Ghost Mode | Make window click-through |
| `Alt + Z` | Toggle Visibility | Hide/show entire window |
| `Alt + 1` | 40% Opacity | Transparent overlay |
| `Alt + 2` | 70% Opacity | Semi-transparent |
| `Alt + 3` | 100% Opacity | Fully opaque |

### 🤖 **AI Model Switching**
| Hotkey | Function | Description |
|--------|----------|-------------|
| `Alt + Q` | Primary Model | Switch to primary AI |
| `Alt + W` | Secondary Model | Switch to secondary AI |
| `Alt + E` | Auto-Select | Choose best available model |

### 👁️ **Vision AI Controls**
| Hotkey | Function | Description |
|--------|----------|-------------|
| `Alt + V` | Toggle Vision Mode | Enter/exit screenshot analysis |
| `Alt + S` | Capture Screenshot | Take screenshot for analysis |
| `Alt + P` | Process Screenshots | Analyze captured screenshots |
| `Alt + R` | Reset Queue | Clear all screenshots |

### 🎤 **Audio Controls**
| Hotkey | Function | Description |
|--------|----------|-------------|
| `Alt + M` | Toggle Mic Mute | Mute/unmute microphone |
| `Alt + U` | Universal Pause | Pause all AI processing |

---

## 👁️ Vision AI Capabilities

### 🎯 **Supported Content Types**
- **Coding Problems** - LeetCode, HackerRank, interview questions
- **Database Schemas** - Table structures, ER diagrams, SQL requirements
- **System Architecture** - High-level design diagrams
- **Algorithms** - Flowcharts, complexity analysis
- **Code Snippets** - Multi-language code review

### 🔍 **Analysis Features**
- **Multi-approach Solutions** - Always provides 2+ different approaches
- **Complete Implementations** - Production-ready code with comments
- **Complexity Analysis** - Time and space complexity for each solution
- **Interview Tips** - How to present solutions effectively
- **Edge Case Handling** - Comprehensive test scenarios

### 📸 **Usage Workflow**
1. **Enter Vision Mode** (`Alt + V`) - Pauses audio processing
2. **Capture Screenshots** (`Alt + S`) - Up to 4 screenshots in queue
3. **Analyze Problems** (`Alt + P`) - AI processes all screenshots as one complete problem
4. **Get Solutions** - Receive detailed analysis with multiple approaches
5. **Ask Follow-ups** - Reference analysis in future conversation

---

## 🗄️ SQL Support

### 📊 **Database Analysis**
- **Automatic Detection** - Recognizes database schemas and SQL requirements
- **Table Documentation** - Extracts and formats table structures
- **Relationship Mapping** - Identifies foreign keys and constraints
- **Query Generation** - Provides multiple SQL solution approaches

### 💾 **SQL Features**
- **Smart Recognition** - Only analyzes SQL when database content detected
- **Multi-approach Queries** - Different optimization strategies
- **Performance Tips** - Indexing and scalability recommendations
- **Edge Case Handling** - NULL values, empty results, data validation

## 🎯 Usage Guide

### 🌟 **Complete Interview Flow**

#### **Phase 1: Setup & Onboarding**
1. **Profile Configuration**
   - Enter your name, target company, and role
   - Paste complete resume (unlimited length)
   - Add job description and requirements
   - Select interview focus areas

2. **AI Model Selection**
   - Choose primary AI provider and model
   - Optional: Select secondary model for fallback
   - Configure vision AI for screenshot analysis
   - Select preferred programming languages

#### **Phase 2: Pre-Flight Checks**
- ✅ Microphone permissions and selection
- ✅ AI provider connectivity verification
- ✅ Vision model availability (if enabled)
- ✅ Audio processing pipeline test

#### **Phase 3: Live Interview**
1. **Start Session** - Real-time transcription begins
2. **AI Assistance** - Get intelligent responses to questions
3. **Vision Analysis** - Screenshot and analyze complex problems
4. **Model Switching** - Change AI providers as needed
5. **Context Tracking** - All conversations remembered for reference

### 🎨 **Advanced Features**

#### **Context Management**
- **Persistent Profile** - Your background never leaves context
- **Conversation History** - Last 6 exchanges fully preserved
- **Cross-Referencing** - Ask about previous questions anytime
- **No Truncation** - Full responses stored (up to 128k tokens)

#### **Smart Audio Processing**
- **Intelligent Buffering** - Waits for complete thoughts
- **Noise Handling** - Robust against audio interruptions
- **Configurable Processing** - All speakers or interviewer-only

---

## 🔧 Configuration

### 📁 **Environment Variables (.env)**
```bash
# API Keys
DEEPGRAM_API_KEY=your_deepgram_key_here

# AI Configuration  
TRACK_CANDIDATE_RESPONSES=true
INCLUDE_CONVERSATION_HISTORY=true
MAX_CONVERSATION_HISTORY=6
GENERATE_FULL_ANSWERS=true
PERSONALIZE_ANSWERS=true

# System Settings
DEV_MODE=false
LOG_LEVEL=INFO
ENABLE_SYSTEM_TRAY=true
START_IN_STEALTH_MODE=false
```

### 🤖 **AI Providers (ai_providers.json)**
```json
{
  "name": "Groq",
  "baseURL": "https://api.groq.com/openai/v1",
  "apiKey": "your_groq_key",
  "models": ["llama-3.3-70b", "llama-4-maverick-17b"],
  "supportsVision": true,
  "visionModels": ["llama-4-scout-17b", "llama-4-maverick-17b"],
  "default": true
}
```

### ⚙️ **Advanced Settings**
- **Conversation History**: 6-20 exchanges (configurable)
- **Token Limits**: 4k (regular) / 8k (vision) responses
- **Context Window**: 128k+ tokens supported
- **Audio Buffer**: 1.3s silence detection
- **Screenshot Queue**: Up to 4 images

---

## 🏗️ Architecture

### 🎯 **System Overview**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend UI   │◄──►│   WebSocket API  │◄──►│  LLM Services   │
│                 │    │                  │    │                 │
│ • Vue.js/HTML   │    │ • FastAPI        │    │ • Multi-Provider│
│ • Real-time UI  │    │ • Event Handling │    │ • Health Checks │
│ • Vision Queue  │    │ • State Mgmt     │    │ • Failover      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Global Hotkeys  │    │ Context Manager  │    │ Vision Service  │
│                 │    │                  │    │                 │
│ • System-wide   │    │ • Conversation   │    │ • Screenshot    │
│ • Window Mgmt   │    │ • Persistent     │    │ • Multi-Model   │
│ • Audio Control │    │ • Memory Mgmt    │    │ • Smart Analysis│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 🔄 **Data Flow**
1. **Audio Input** → Deepgram STT → Transcript Processing
2. **User Question** → Context Manager → LLM Service → AI Response
3. **Screenshot** → Vision Service → Analysis → Context Storage
4. **Global Hotkey** → Command Router → Feature Execution

### 🧠 **Context Management**
- **Persistent Layer**: Resume, job description, candidate profile (unlimited)
- **Conversation Layer**: Recent exchanges with full responses (6+ exchanges)
- **Session Layer**: Current question, active features, model state

---

## 📚 API Documentation

### 🔌 **WebSocket Events**

#### **Client → Server**
```javascript
// Start interview session
{
  "type": "start_interview",
  "payload": {
    "aiProvider": { "name": "Groq", "model": "llama-3.3-70b" },
    "onboardingData": { /* profile data */ },
    "visionConfig": { "provider": "Groq", "model": "llama-4-scout" }
  }
}

// Vision analysis request
{
  "type": "vision_analysis", 
  "payload": {
    "screenshots": ["data:image/png;base64,..."],
    "languages": ["python", "sql"],
    "visionConfig": { "provider": "Groq", "model": "llama-4-scout" }
  }
}
```

#### **Server → Client**
```javascript
// AI response
{
  "type": "ai_answer",
  "payload": {
    "answer": "Complete AI response...",
    "preset_used": { "provider": "Groq", "model": "llama-3.3-70b" },
    "success": true
  }
}

// Vision analysis result
{
  "type": "vision_analysis_result",
  "payload": {
    "success": true,
    "analysis": "Complete problem analysis...",
    "screenshot_count": 3,
    "languages": ["python", "sql"]
  }
}
```

### 🛠️ **REST API Endpoints**

#### **Configuration**
```http
GET /api/ai-providers          # Get available AI providers
GET /api/config               # Get current configuration
POST /api/transparency        # Set window transparency
POST /api/transparency/presets/{level}  # Quick transparency presets
```

---

## 🚀 Advanced Features

### 🎯 **Interview Scenarios**

#### **Coding Interview**
1. **Problem Analysis** - Vision AI reads problem statement
2. **Multiple Solutions** - Get 2+ approaches with complexity analysis
3. **Code Implementation** - Production-ready code in your preferred language
4. **Optimization Discussion** - Follow-up questions with context awareness
5. **Cross-Language** - Ask for same solution in different languages

#### **System Design Interview**
1. **Requirement Analysis** - Break down system requirements
2. **Architecture Design** - High-level and detailed component design
3. **Scalability Discussion** - Handle growth and performance bottlenecks
4. **Technology Choices** - Database, caching, load balancing decisions
5. **Trade-off Analysis** - Discuss pros/cons of different approaches

#### **Database Interview**
1. **Schema Analysis** - Vision AI reads table structures and relationships
2. **Query Writing** - Multiple SQL approaches for complex requirements
3. **Performance Optimization** - Indexing and query optimization strategies
4. **Data Modeling** - Design decisions and normalization
5. **Scalability** - Handling large datasets and concurrent access

### 🔒 **Privacy & Security**

#### **Data Protection**
- **Local Processing** - All conversation data stays on your machine
- **API Security** - Encrypted communications with AI providers
- **No Data Persistence** - Conversation history cleared between sessions
- **Screen Protection** - Hidden from screen recordings and sharing

#### **Stealth Features**
- **Invisible Recording** - Appears as black rectangle in screen captures
- **Taskbar Hiding** - Completely hidden from task switcher
- **Ghost Mode** - Click-through window for ultimate discretion
- **Quick Hide** - Instant window hiding with global hotkey

---

## 🎨 User Interface

### 🖥️ **Main Interface**
- **Clean, Modern Design** - Minimal distraction during interviews
- **Real-time Status** - Live indicators for transcription and AI processing
- **Visual Queue Management** - Screenshot thumbnails with preview
- **Responsive Layout** - Adapts to different screen sizes

### 📱 **Mobile-Friendly**
- **Touch-Optimized** controls for tablet use
- **Responsive Design** scales to any screen size
- **Gesture Support** for screenshot management

### 🎨 **Customization**
- **Transparency Levels** - 5 different opacity settings
- **Always on Top** - Stays visible over other applications
- **Flexible Positioning** - Resize and move as needed

---

## 🔧 Troubleshooting

### 🎤 **Audio Issues**
```bash
# Check microphone permissions
# Windows: Settings > Privacy > Microphone > Allow apps to access microphone

# Verify Deepgram API key
echo $DEEPGRAM_API_KEY

# Test audio device
python -c "import pyaudio; print([pyaudio.PyAudio().get_device_info_by_index(i)['name'] for i in range(pyaudio.PyAudio().get_device_count())])"
```

### 🤖 **AI Provider Issues**
```bash
# Test API connectivity
curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/openai/v1/models

# Check provider health in application logs
tail -f aura.log | grep "Health check"

# Verify model availability
grep -A 5 "models" ai_providers.json
```

### 👁️ **Vision AI Issues**
```bash
# Check vision model support
grep -A 3 "visionModels" ai_providers.json

# Verify screenshot capture
# Ensure screen sharing permissions are granted

# Test vision API
curl -X POST -H "Authorization: Bearer $API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"llama-4-scout","messages":[{"role":"user","content":[{"type":"text","text":"Hello"}]}]}' \
     https://api.groq.com/openai/v1/chat/completions
```

---

## 📈 Performance Optimization

### ⚡ **Speed Improvements**
- **Provider Selection** - Choose fastest models for quick responses
- **Parallel Processing** - Multiple AI requests handled simultaneously  
- **Smart Caching** - Repeated questions use cached contexts
- **Optimized Prompts** - Structured prompts for faster processing

### 💾 **Memory Management**
- **Conversation Limits** - Configurable history length (default: 6 exchanges)
- **Context Optimization** - Only relevant context sent to AI
- **Resource Cleanup** - Automatic cleanup of temporary files
- **Smart Buffering** - Efficient audio and image processing

### 🌐 **Network Optimization**
- **Connection Pooling** - Reuse connections to AI providers
- **Retry Logic** - Automatic retry with exponential backoff
- **Health Monitoring** - Real-time provider availability tracking
- **Failover** - Seamless switching between providers

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### 🐛 **Bug Reports**
- Use GitHub Issues with detailed reproduction steps
- Include system information and logs
- Provide screenshots for UI issues

### 💡 **Feature Requests**
- Describe the use case and expected behavior
- Consider implementation complexity
- Provide mockups for UI changes

### 🔧 **Development Setup**
```bash
# Clone and setup development environment
git clone https://github.com/yourusername/aura-ai-interview-coach.git
cd aura-ai-interview-coach

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Start development server with hot reload
python main.py --dev
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Deepgram** - For excellent speech-to-text capabilities
- **Groq** - For fast inference and vision AI models
- **Cerebras** - For high-performance language models
- **Google Gemini** - For advanced AI capabilities
- **FastAPI** - For the robust web framework
- **Community** - For feedback and contributions

---

## 📞 Support

### 🆘 **Getting Help**
- 📚 [Documentation](https://github.com/yourusername/aura-ai-interview-coach/wiki)
- 💬 [Discussions](https://github.com/yourusername/aura-ai-interview-coach/discussions)
- 🐛 [Issues](https://github.com/yourusername/aura-ai-interview-coach/issues)
- 📧 [Email Support](mailto:support@aura-ai.com)

### 🌟 **Show Your Support**
If this project helped you ace your interviews, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs and issues  
- 💡 Suggesting new features
- 🤝 Contributing code or documentation
- 📢 Sharing with others

---

<div align="center">

**Made with ❤️ for interview success**

[⬆ Back to Top](#-aura-ai-interview-coach)

</div> 