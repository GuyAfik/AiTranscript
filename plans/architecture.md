# AiTranscript - System Architecture Document

## 1. Executive Summary

AiTranscript is a voice transcription tool with AI-powered cleanup capabilities. The system accepts three input methods: YouTube URLs, audio file uploads, and live voice recordings. It transcribes audio using a local Whisper model and provides AI-powered summaries using OpenAI's GPT-4/5 API.

**Key Design Decisions:**
- **Framework**: Streamlit (Python) - simplifies UI development and deployment
- **Transcription**: Local Whisper model - cost-effective, privacy-friendly
- **AI Cleanup**: OpenAI GPT-4/5 API - high-quality summarization
- **Architecture**: Service-oriented with clear separation of concerns
- **Deployment**: Streamlit Cloud, Render, or similar Python-supporting platforms

---

## 2. System Architecture Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   YouTube    │  │  File Upload │  │    Voice     │      │
│  │   Input      │  │    Input     │  │  Recording   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Main Application Controller             │   │
│  │         (Orchestrates service interactions)          │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │                                      │
│         ┌─────────────┼─────────────┐                       │
│         ▼             ▼             ▼                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ YouTube  │  │  Audio   │  │   AI     │                  │
│  │ Service  │  │Transcribe│  │ Cleanup  │                  │
│  │          │  │ Service  │  │ Service  │                  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                  │
└───────┼─────────────┼─────────────┼────────────────────────┘
        │             │             │
        ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   YouTube    │  │    Whisper   │  │   OpenAI     │      │
│  │  Transcript  │  │    (Local)   │  │   GPT API    │      │
│  │     API      │  │              │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| **Streamlit Frontend** | User interface, input collection, result display |
| **Application Controller** | Orchestrates service calls, manages application flow |
| **YouTube Service** | Extracts transcripts from YouTube videos |
| **Audio Transcription Service** | Handles audio file processing and transcription |
| **AI Cleanup Service** | Summarizes and cleans up transcribed text |
| **External Services** | Third-party APIs and local models |

---

## 3. Service Layer Architecture

### 3.1 YouTube Transcript Service

**Purpose**: Extract transcripts from YouTube videos using video URLs

**Responsibilities**:
- Validate YouTube URL format
- Extract video ID from URL
- Fetch transcript using youtube-transcript-api
- Handle multiple language transcripts
- Error handling for unavailable transcripts

**Key Methods**:
```python
class YouTubeService:
    def validate_url(url: str) -> bool
    def extract_video_id(url: str) -> str
    def get_transcript(video_id: str, languages: list) -> str
    def get_available_languages(video_id: str) -> list
```

**Dependencies**:
- `youtube-transcript-api`

**Error Scenarios**:
- Invalid URL format
- Video not found
- Transcript not available
- Network errors

---

### 3.2 Audio Transcription Service

**Purpose**: Transcribe audio files and live recordings using local Whisper model

**Responsibilities**:
- Accept multiple audio formats (mp3, wav, m4a, ogg, flac)
- Convert audio to compatible format if needed
- Load and manage Whisper model
- Transcribe audio to text
- Handle temporary file storage
- Clean up temporary files

**Key Methods**:
```python
class AudioTranscriptionService:
    def __init__(model_size: str = "base")
    def load_model() -> whisper.Model
    def validate_audio_file(file) -> bool
    def transcribe_file(audio_file) -> str
    def transcribe_audio_data(audio_bytes: bytes) -> str
    def cleanup_temp_files(file_path: str)
```

**Model Size Options**:
- `tiny` - Fastest, least accurate (~1GB RAM)
- `base` - Balanced (default) (~1GB RAM)
- `small` - Better accuracy (~2GB RAM)
- `medium` - High accuracy (~5GB RAM)
- `large` - Best accuracy (~10GB RAM)

**Dependencies**:
- `openai-whisper`
- `ffmpeg-python` (for audio format conversion)
- `pydub` (audio processing)

**Error Scenarios**:
- Unsupported file format
- Corrupted audio file
- Insufficient memory for model
- Transcription timeout

---

### 3.3 Voice Recording Service

**Purpose**: Handle browser-based voice recording functionality

**Responsibilities**:
- Provide recording interface through Streamlit
- Capture audio from browser microphone
- Convert recorded audio to processable format
- Pass audio to transcription service

**Key Methods**:
```python
class VoiceRecordingService:
    def initialize_recorder() -> AudioRecorder
    def start_recording()
    def stop_recording() -> bytes
    def get_audio_data() -> bytes
```

**Dependencies**:
- `streamlit-audiorecorder` or `st-audiorec`
- Browser MediaRecorder API (client-side)

**Error Scenarios**:
- Microphone permission denied
- No audio input device
- Recording timeout
- Browser compatibility issues

---

### 3.4 AI Cleanup Service

**Purpose**: Summarize and clean up transcribed text using OpenAI GPT API

**Responsibilities**:
- Format transcripts for AI processing
- Send requests to OpenAI API
- Parse and format AI responses
- Handle API rate limits and errors
- Manage API key configuration

**Key Methods**:
```python
class AICleanupService:
    def __init__(api_key: str, model: str = "gpt-4")
    def summarize_text(text: str, max_length: int) -> str
    def clean_transcript(text: str) -> str
    def generate_key_points(text: str) -> list
    def custom_prompt(text: str, prompt: str) -> str
```

**Prompt Templates**:
- **Summary**: "Provide a concise summary of the following transcript..."
- **Cleanup**: "Clean up this transcript by removing filler words..."
- **Key Points**: "Extract the main points from this transcript..."

**Dependencies**:
- `openai` (Python SDK)

**Error Scenarios**:
- Invalid API key
- Rate limit exceeded
- API timeout
- Token limit exceeded
- Network errors

---

## 4. Streamlit UI Design

### 4.1 Page Layout

```
┌─────────────────────────────────────────────────────────┐
│                    AiTranscript                          │
│              Voice Transcription & AI Cleanup            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Tab 1: YouTube  │ Tab 2: Upload │ Tab 3: Record│   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  [Input Area - varies by tab]                           │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Settings (Expandable)                           │   │
│  │  - Whisper Model Size: [base ▼]                 │   │
│  │  - Summary Length: [medium ▼]                   │   │
│  │  - Language: [auto-detect ▼]                    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  [Process Button]                                       │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Results (Appears after processing)              │   │
│  │                                                  │   │
│  │  📝 Full Transcript                              │   │
│  │  [Transcript text in expandable section]        │   │
│  │                                                  │   │
│  │  ✨ AI Summary                                   │   │
│  │  [Summary text]                                  │   │
│  │                                                  │   │
│  │  🔑 Key Points                                   │   │
│  │  • Point 1                                       │   │
│  │  • Point 2                                       │   │
│  │                                                  │   │
│  │  [Download Transcript] [Download Summary]       │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 4.2 UI Components by Tab

**Tab 1: YouTube Transcription**
- Text input for YouTube URL
- Language selection dropdown
- "Get Transcript" button
- Progress indicator

**Tab 2: File Upload**
- File uploader (accepts mp3, wav, m4a, ogg, flac)
- File size indicator
- Audio player preview
- "Transcribe" button
- Progress indicator

**Tab 3: Voice Recording**
- Audio recorder component
- Recording status indicator
- Duration counter
- "Start/Stop Recording" button
- Audio playback preview
- "Transcribe Recording" button
- Progress indicator

### 4.3 State Management

Streamlit session state will manage:
- Current tab selection
- User settings (model size, language, etc.)
- Processing status
- Transcript results
- Summary results
- Error messages

---

## 5. Data Flow Diagrams

### 5.1 YouTube Transcription Flow

```
User Input (URL)
      │
      ▼
┌─────────────────┐
│ Validate URL    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Extract Video ID│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Fetch Transcript│
│ (YouTube API)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Display Full    │
│ Transcript      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Send to GPT API │
│ for Summary     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Display Summary │
│ & Key Points    │
└─────────────────┘
```

### 5.2 Audio File Upload Flow

```
User Upload (File)
      │
      ▼
┌─────────────────┐
│ Validate File   │
│ (format, size)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Save to Temp    │
│ Storage         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Load Whisper    │
│ Model (cached)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Transcribe Audio│
│ (Local Whisper) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Cleanup Temp    │
│ Files           │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Display Full    │
│ Transcript      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Send to GPT API │
│ for Summary     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Display Summary │
│ & Key Points    │
└─────────────────┘
```

### 5.3 Voice Recording Flow

```
User Action (Record)
      │
      ▼
┌─────────────────┐
│ Initialize      │
│ Audio Recorder  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Capture Audio   │
│ from Browser    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Stop Recording  │
│ Get Audio Bytes │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Convert to      │
│ Compatible      │
│ Format          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Load Whisper    │
│ Model (cached)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Transcribe Audio│
│ (Local Whisper) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Display Full    │
│ Transcript      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Send to GPT API │
│ for Summary     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Display Summary │
│ & Key Points    │
└─────────────────┘
```

---

## 6. Project Structure

```
aitranscript/
│
├── .streamlit/
│   └── config.toml              # Streamlit configuration
│
├── src/
│   ├── __init__.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── youtube_service.py       # YouTube transcript extraction
│   │   ├── audio_service.py         # Audio transcription (Whisper)
│   │   ├── recording_service.py     # Voice recording handling
│   │   └── ai_service.py            # AI cleanup and summarization
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py            # Input validation utilities
│   │   ├── file_handler.py          # File operations and cleanup
│   │   └── config.py                # Configuration management
│   │
│   └── ui/
│       ├── __init__.py
│       ├── components.py            # Reusable UI components
│       └── styles.py                # Custom CSS styles
│
├── app.py                       # Main Streamlit application
├── requirements.txt             # Python dependencies
├── pyproject.toml              # uv project configuration
├── .env.example                # Environment variables template
├── .gitignore
├── README.md
├── Dockerfile                  # Docker configuration
└── docker-compose.yml          # Docker Compose setup
```

### 6.1 File Descriptions

**Core Application**:
- `app.py`: Main entry point, Streamlit UI layout and orchestration
- `.streamlit/config.toml`: Streamlit theme and server configuration

**Services Layer**:
- `youtube_service.py`: YouTube transcript extraction logic
- `audio_service.py`: Whisper model management and transcription
- `recording_service.py`: Browser recording integration
- `ai_service.py`: OpenAI API integration for summarization

**Utilities**:
- `validators.py`: Input validation (URLs, files, formats)
- `file_handler.py`: Temporary file management and cleanup
- `config.py`: Environment variables and settings management

**UI Components**:
- `components.py`: Reusable Streamlit components
- `styles.py`: Custom CSS for enhanced UI

**Configuration**:
- `requirements.txt`: Python package dependencies
- `pyproject.toml`: uv package manager configuration
- `.env.example`: Template for environment variables
- `Dockerfile`: Container configuration for deployment

---

## 7. Technology Stack & Dependencies

### 7.1 Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Primary language |
| Streamlit | 1.29+ | Web framework and UI |
| uv | latest | Fast Python package manager |

### 7.2 Key Dependencies

**Transcription & Audio Processing**:
```
openai-whisper==20231117
ffmpeg-python==0.2.0
pydub==0.25.1
```

**YouTube Integration**:
```
youtube-transcript-api==0.6.1
```

**AI Services**:
```
openai==1.6.1
```

**Streamlit Extensions**:
```
streamlit-audiorecorder==0.0.5
# OR
st-audiorec==0.1.0
```

**Utilities**:
```
python-dotenv==1.0.0
validators==0.22.0
```

### 7.3 System Requirements

**Minimum**:
- Python 3.10+
- 4GB RAM (for Whisper base model)
- 2GB disk space
- FFmpeg installed

**Recommended**:
- Python 3.11+
- 8GB RAM (for Whisper small/medium models)
- 5GB disk space
- GPU support (optional, for faster transcription)

### 7.4 External Services

**Required**:
- OpenAI API account and API key (for GPT-4/5 summarization)

**Optional**:
- YouTube Data API key (if transcript-api rate limited)

---

## 8. Configuration Management

### 8.1 Environment Variables

```bash
# .env file structure

# OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=2000

# Whisper Configuration
WHISPER_MODEL_SIZE=base
WHISPER_DEVICE=cpu  # or 'cuda' for GPU

# Application Settings
MAX_FILE_SIZE_MB=100
TEMP_FILE_RETENTION_HOURS=1
SUPPORTED_AUDIO_FORMATS=mp3,wav,m4a,ogg,flac

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
```

### 8.2 Configuration Loading

```python
# src/utils/config.py structure

class Config:
    # OpenAI settings
    OPENAI_API_KEY: str
    OPENAI_MODEL: str
    
    # Whisper settings
    WHISPER_MODEL_SIZE: str
    WHISPER_DEVICE: str
    
    # Application settings
    MAX_FILE_SIZE_MB: int
    TEMP_DIR: Path
    
    @classmethod
    def load_from_env()
    
    @classmethod
    def validate()
```

---

## 9. Error Handling Strategy

### 9.1 Error Categories

**User Input Errors**:
- Invalid YouTube URL format
- Unsupported file format
- File size exceeds limit
- Empty or corrupted audio

**Service Errors**:
- YouTube transcript unavailable
- Whisper model loading failure
- OpenAI API errors (rate limit, invalid key)
- Network connectivity issues

**System Errors**:
- Insufficient memory
- Disk space issues
- FFmpeg not installed
- Permission errors

### 9.2 Error Handling Approach

```python
# Error handling pattern

class TranscriptionError(Exception):
    """Base exception for transcription errors"""
    pass

class YouTubeError(TranscriptionError):
    """YouTube-specific errors"""
    pass

class WhisperError(TranscriptionError):
    """Whisper transcription errors"""
    pass

class AIServiceError(TranscriptionError):
    """AI service errors"""
    pass

# In services:
try:
    result = service.process()
except SpecificError as e:
    logger.error(f"Error: {e}")
    st.error(f"User-friendly message: {e}")
    # Provide recovery suggestions
```

### 9.3 User Feedback

- **Success**: Green success message with results
- **Warning**: Yellow warning for non-critical issues
- **Error**: Red error message with actionable suggestions
- **Info**: Blue info messages for processing status

### 9.4 Logging Strategy

```python
# Logging configuration

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aitranscript.log'),
        logging.StreamHandler()
    ]
)

# Log levels:
# DEBUG: Detailed diagnostic information
# INFO: General informational messages
# WARNING: Warning messages for recoverable issues
# ERROR: Error messages for failures
# CRITICAL: Critical errors requiring immediate attention
```

---

## 10. Deployment Strategy

### 10.1 Deployment Options

**Option 1: Streamlit Cloud (Recommended for MVP)**
- **Pros**: Free tier, easy deployment, automatic HTTPS
- **Cons**: Limited resources, public by default
- **Setup**: Connect GitHub repo, configure secrets
- **Cost**: Free (with limitations)

**Option 2: Render**
- **Pros**: Free tier, Docker support, custom domains
- **Cons**: Cold starts on free tier
- **Setup**: Deploy from GitHub, configure environment
- **Cost**: Free tier available

**Option 3: Railway**
- **Pros**: Easy deployment, good free tier
- **Cons**: Credit-based pricing
- **Setup**: Connect repo, configure services
- **Cost**: $5 credit/month free

**Option 4: Fly.io**
- **Pros**: Global deployment, Docker-native
- **Cons**: More complex setup
- **Setup**: Dockerfile deployment
- **Cost**: Free tier available

**Option 5: Self-Hosted (Docker)**
- **Pros**: Full control, no vendor lock-in
- **Cons**: Requires server management
- **Setup**: Docker Compose deployment
- **Cost**: Server costs only

### 10.2 Recommended Deployment: Streamlit Cloud

**Steps**:
1. Push code to GitHub repository
2. Sign up for Streamlit Cloud
3. Connect GitHub repository
4. Configure secrets (OpenAI API key)
5. Deploy application
6. Monitor usage and performance

**Secrets Configuration**:
```toml
# Streamlit Cloud secrets

[secrets]
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-4-turbo-preview"
WHISPER_MODEL_SIZE = "base"
```

### 10.3 Docker Deployment

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  aitranscript:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - WHISPER_MODEL_SIZE=base
    volumes:
      - ./temp:/app/temp
    restart: unless-stopped
```

### 10.4 Performance Considerations

**Whisper Model Caching**:
- Cache loaded models in memory
- Use `@st.cache_resource` for model loading
- Consider model size vs. accuracy tradeoff

**API Rate Limiting**:
- Implement request throttling for OpenAI API
- Handle rate limit errors gracefully
- Consider caching summaries for identical transcripts

**File Handling**:
- Implement automatic cleanup of temporary files
- Set maximum file size limits
- Use streaming for large files

**Memory Management**:
- Monitor memory usage with large audio files
- Implement chunking for very long recordings
- Clear session state when appropriate

---

## 11. Security Considerations

### 11.1 API Key Management

- Store API keys in environment variables
- Never commit API keys to version control
- Use `.env.example` for documentation
- Rotate keys periodically

### 11.2 File Upload Security

- Validate file types and extensions
- Scan for malicious content
- Limit file sizes
- Sanitize filenames
- Implement virus scanning (optional)

### 11.3 Data Privacy

- No persistent storage of user data
- Automatic cleanup of temporary files
- Clear session data on completion
- HTTPS for all communications
- Comply with data protection regulations

### 11.4 Rate Limiting

- Implement per-user rate limits
- Prevent API abuse
- Monitor usage patterns
- Set quotas for free tier

---

## 12. Scalability & Maintainability

### 12.1 Scalability Considerations

**Current Design (Single User)**:
- Suitable for personal use or small teams
- Runs on single server instance
- Limited by server resources

**Future Scalability Options**:
- **Horizontal Scaling**: Deploy multiple instances behind load balancer
- **Queue System**: Add Celery/RQ for background processing
- **Caching**: Implement Redis for transcript caching
- **CDN**: Use CDN for static assets
- **Database**: Add PostgreSQL for user history (future feature)

### 12.2 Maintainability Features

**Code Organization**:
- Clear separation of concerns
- Service-oriented architecture
- Modular design for easy updates
- Comprehensive documentation

**Testing Strategy** (Future):
- Unit tests for services
- Integration tests for workflows
- End-to-end tests for UI
- Mock external API calls

**Monitoring** (Future):
- Application performance monitoring
- Error tracking (Sentry)
- Usage analytics
- API quota monitoring

### 12.3 Future Enhancements

**Phase 2 Features**:
- User authentication and accounts
- Transcript history and search
- Multiple language support
- Custom AI prompts
- Batch processing
- Export formats (PDF, DOCX)

**Phase 3 Features**:
- Real-time collaboration
- Speaker diarization
- Timestamp navigation
- Video player integration
- Mobile app

---

## 13. Development Workflow

### 13.1 Local Development Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd aitranscript

# 2. Create virtual environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
uv pip install -r requirements.txt

# 4. Install FFmpeg (system dependency)
# macOS: brew install ffmpeg
# Ubuntu: sudo apt-get install ffmpeg
# Windows: Download from ffmpeg.org

# 5. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 6. Run application
streamlit run app.py
```

### 13.2 Development Best Practices

- Use type hints for all functions
- Write docstrings for all classes and methods
- Follow PEP 8 style guide
- Use meaningful variable names
- Keep functions small and focused
- Comment complex logic
- Use logging instead of print statements

### 13.3 Git Workflow

```
main (production)
  ↑
develop (integration)
  ↑
feature/* (new features)
bugfix/* (bug fixes)
```

---

## 14. API Specifications (Internal)

### 14.1 YouTube Service API

```python
class YouTubeService:
    """
    Service for extracting transcripts from YouTube videos.
    """
    
    def get_transcript(
        self,
        url: str,
        languages: list[str] = ['en']
    ) -> dict:
        """
        Extract transcript from YouTube video.
        
        Args:
            url: YouTube video URL
            languages: Preferred languages (default: ['en'])
            
        Returns:
            {
                'text': str,           # Full transcript text
                'language': str,       # Detected language
                'duration': float,     # Video duration in seconds
                'segments': list       # Individual transcript segments
            }
            
        Raises:
            YouTubeError: If transcript unavailable or URL invalid
        """
```

### 14.2 Audio Transcription Service API

```python
class AudioTranscriptionService:
    """
    Service for transcribing audio files using Whisper.
    """
    
    def transcribe(
        self,
        audio_source: Union[str, bytes],
        language: Optional[str] = None
    ) -> dict:
        """
        Transcribe audio to text.
        
        Args:
            audio_source: File path or audio bytes
            language: Language code (None for auto-detect)
            
        Returns:
            {
                'text': str,           # Full transcription
                'language': str,       # Detected language
                'segments': list,      # Timestamped segments
                'duration': float      # Audio duration
            }
            
        Raises:
            WhisperError: If transcription fails
        """
```

### 14.3 AI Cleanup Service API

```python
class AICleanupService:
    """
    Service for AI-powered text summarization and cleanup.
    """
    
    def summarize(
        self,
        text: str,
        style: str = 'concise'
    ) -> dict:
        """
        Generate AI summary of transcript.
        
        Args:
            text: Transcript text to summarize
            style: Summary style ('concise', 'detailed', 'bullet')
            
        Returns:
            {
                'summary': str,        # Main summary
                'key_points': list,    # Key takeaways
                'word_count': int,     # Original word count
                'summary_ratio': float # Compression ratio
            }
            
        Raises:
            AIServiceError: If API call fails
        """
```

---

## 15. Conclusion

This architecture provides a solid foundation for the AiTranscript application with the following key strengths:

**Strengths**:
1. **Simplicity**: Streamlit framework reduces complexity
2. **Modularity**: Clear service separation enables easy maintenance
3. **Cost-Effective**: Local Whisper reduces API costs
4. **Scalable**: Architecture supports future enhancements
5. **User-Friendly**: Intuitive UI with minimal learning curve

**Trade-offs**:
1. **No Persistence**: Stateless design (can be added later)
2. **Single Instance**: Not designed for high concurrency initially
3. **Resource Intensive**: Whisper requires significant memory

**Next Steps**:
1. Review and approve architecture
2. Set up development environment
3. Implement core services
4. Build Streamlit UI
5. Test and iterate
6. Deploy to chosen platform

This architecture is designed to be implemented incrementally, starting with core functionality and expanding based on user feedback and requirements.

---

## Appendix A: Whisper Model Comparison

| Model | Size | RAM | Speed | Accuracy | Use Case |
|-------|------|-----|-------|----------|----------|
| tiny | 39M | ~1GB | Fastest | Lowest | Quick drafts |
| base | 74M | ~1GB | Fast | Good | Default choice |
| small | 244M | ~2GB | Medium | Better | Quality focus |
| medium | 769M | ~5GB | Slow | High | Professional |
| large | 1550M | ~10GB | Slowest | Best | Maximum accuracy |

## Appendix B: OpenAI Model Comparison

| Model | Cost/1K tokens | Speed | Quality | Use Case |
|-------|---------------|-------|---------|----------|
| gpt-3.5-turbo | $0.0015 | Fast | Good | Cost-effective |
| gpt-4-turbo | $0.01 | Medium | Excellent | Recommended |
| gpt-4 | $0.03 | Slow | Best | Premium quality |

## Appendix C: Deployment Cost Estimates

**Streamlit Cloud (Free Tier)**:
- Cost: $0/month
- Limitations: 1GB RAM, public apps
- Best for: MVP and testing

**Render (Starter)**:
- Cost: $7/month
- Resources: 512MB RAM
- Best for: Small-scale production

**Railway (Hobby)**:
- Cost: ~$5-10/month
- Resources: Based on usage
- Best for: Flexible scaling

**Self-Hosted (DigitalOcean)**:
- Cost: $12-24/month
- Resources: 2-4GB RAM
- Best for: Full control

**API Costs (Estimated)**:
- OpenAI GPT-4: ~$0.10-0.50 per transcript
- Whisper (local): $0 (compute only)
- YouTube API: Free (using transcript-api)