# 🎙️ AiTranscript

Voice transcription tool with AI-powered cleanup capabilities. Transcribe audio from YouTube videos, uploaded files, or live recordings, with intelligent summarization using OpenAI GPT.

## ✨ Features

- **Multiple Input Methods**:
  - YouTube URL transcription
  - Audio file upload (mp3, wav, m4a, ogg, flac)
  - Live voice recording

- **Local Transcription**: Uses Whisper model locally for privacy and cost-effectiveness
- **AI-Powered Summaries**: Leverages OpenAI GPT-4/5 for intelligent text summarization
- **User-Friendly Interface**: Built with Streamlit for an intuitive web experience

## 🏗️ Architecture

AiTranscript follows a service-oriented architecture with clear separation of concerns:

- **Services Layer**: YouTube extraction, audio transcription, AI summarization
- **Utils Layer**: Input validation, file handling
- **UI Layer**: Reusable Streamlit components

For detailed architecture information, see [`plans/architecture.md`](plans/architecture.md).

## 📋 Prerequisites

- **Python**: 3.11 or higher
- **FFmpeg**: Required for audio processing
- **OpenAI API Key**: For AI summarization features

### Installing FFmpeg

**macOS**:
```bash
brew install ffmpeg
```

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Windows**:
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AiTranscript
```

### 2. Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. Create Virtual Environment and Install Dependencies

```bash
# Create virtual environment
uv venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Get your API key from: https://platform.openai.com/api-keys
```

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `WHISPER_MODEL_SIZE`: Whisper model size (default: base)
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-4-turbo-preview)

### 5. Run the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`.

## 📦 Project Structure

```
aitranscript/
├── src/
│   ├── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── youtube_service.py       # YouTube transcript extraction
│   │   ├── audio_service.py         # Audio transcription (Whisper)
│   │   ├── transcription_service.py # Voice recording handling
│   │   └── ai_service.py            # AI cleanup and summarization
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py            # Input validation utilities
│   │   └── file_handler.py          # File operations and cleanup
│   └── ui/
│       ├── __init__.py
│       └── components.py            # Reusable UI components
├── app.py                           # Main Streamlit application
├── pyproject.toml                   # Project configuration
├── .env.example                     # Environment variables template
└── README.md                        # This file
```

## 🔧 Configuration

### Whisper Model Sizes

Choose the appropriate model size based on your needs:

| Model  | Size  | RAM   | Speed    | Accuracy | Use Case           |
|--------|-------|-------|----------|----------|--------------------|
| tiny   | 39M   | ~1GB  | Fastest  | Lowest   | Quick drafts       |
| base   | 74M   | ~1GB  | Fast     | Good     | Default choice     |
| small  | 244M  | ~2GB  | Medium   | Better   | Quality focus      |
| medium | 769M  | ~5GB  | Slow     | High     | Professional       |
| large  | 1550M | ~10GB | Slowest  | Best     | Maximum accuracy   |

Set in `.env`:
```bash
WHISPER_MODEL_SIZE=base
```

### OpenAI Models

| Model            | Cost/1K tokens | Speed  | Quality   | Use Case         |
|------------------|----------------|--------|-----------|------------------|
| gpt-3.5-turbo    | $0.0015        | Fast   | Good      | Cost-effective   |
| gpt-4-turbo      | $0.01          | Medium | Excellent | Recommended      |
| gpt-4            | $0.03          | Slow   | Best      | Premium quality  |

Set in `.env`:
```bash
OPENAI_MODEL=gpt-4-turbo-preview
```

## 🛠️ Development

### Using uv for Package Management

```bash
# Add a new dependency
uv pip install package-name

# Add a development dependency
uv pip install --dev package-name

# Update dependencies
uv pip install --upgrade package-name

# Sync dependencies from pyproject.toml
uv pip sync
```

### Running Tests (Coming Soon)

```bash
pytest
```

### Code Formatting

```bash
# Format code with black
black .

# Lint with ruff
ruff check .
```

## 📝 Usage

1. **YouTube Transcription**:
   - Navigate to the "YouTube" tab
   - Paste a YouTube URL
   - Click "Get Transcript"
   - View transcript and AI summary

2. **File Upload**:
   - Navigate to the "Upload" tab
   - Upload an audio file (mp3, wav, m4a, ogg, flac)
   - Click "Transcribe"
   - View transcript and AI summary

3. **Voice Recording**:
   - Navigate to the "Record" tab
   - Click "Start Recording"
   - Speak into your microphone
   - Click "Stop Recording"
   - Click "Transcribe Recording"
   - View transcript and AI summary

## 🔒 Privacy & Security

- **Local Transcription**: Audio is transcribed locally using Whisper (no data sent to external services)
- **No Data Storage**: Transcripts are not stored permanently
- **Temporary Files**: Automatically cleaned up after processing
- **API Key Security**: Store your OpenAI API key securely in `.env` (never commit to version control)

## 🚢 Deployment

### Streamlit Cloud (Recommended for MVP)

1. Push your code to GitHub
2. Sign up for [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Add your `OPENAI_API_KEY` in the Secrets section
5. Deploy!

### Docker (Coming Soon)

```bash
docker-compose up
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for local transcription
- [Streamlit](https://streamlit.io/) for the web framework
- [OpenAI](https://openai.com/) for GPT API

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

**Built with ❤️ using Streamlit, Whisper, and OpenAI GPT**
