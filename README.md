# 🎙️ AiTranscript

Voice transcription tool with AI-powered cleanup capabilities. Transcribe audio from YouTube videos, uploaded files, or live recordings, with intelligent summarization and message refinement using local LLM or OpenAI GPT.

## ✨ Features

- **Multiple Input Methods**:
  - YouTube URL transcription
  - Audio file upload (mp3, wav, m4a, ogg, flac)
  - Live voice recording

- **Dual AI Processing Modes**:
  - **Summarize Mode**: Get clear, concise summaries of transcripts with key points extraction
  - **Refine Mode**: Transform voice recordings into well-structured, professional messages

- **Flexible AI Providers**:
  - **Local LLM (Default)**: Run AI models on your machine via Ollama - free, private, no API key needed
  - **OpenAI GPT**: Cloud-based option for GPT-4/3.5 models

- **Local Transcription**: Uses Whisper model locally for privacy and cost-effectiveness
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
- **Ollama**: For local LLM (recommended, free)
- **OpenAI API Key**: Optional, only if using OpenAI provider

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

### Installing Ollama (for Local LLM)

**macOS/Linux**:
```bash
curl https://ollama.ai/install.sh | sh
```

**Windows**:
Download from [ollama.ai](https://ollama.ai/download)

**Pull a model**:
```bash
# Start Ollama
ollama serve

# Pull a model (in another terminal)
ollama pull llama2
# or
ollama pull mistral
```

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

# Edit .env if needed (optional - defaults work out of the box)
```

Environment variables (all optional):
- `AI_PROVIDER`: Choose 'local' (default) or 'openai'
- `LOCAL_MODEL`: Local model to use (default: llama2)
- `OPENAI_API_KEY`: Your OpenAI API key (only if using OpenAI)
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-4-turbo-preview)
- `WHISPER_MODEL_SIZE`: Whisper model size (default: base)

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

### AI Provider Models

#### Local LLM Models (via Ollama) - Default & Recommended

| Model      | Size  | RAM   | Speed    | Quality   | Use Case           |
|------------|-------|-------|----------|-----------|-------------------|
| llama2     | 3.8GB | ~8GB  | Fast     | Good      | Default, balanced |
| llama3     | 4.7GB | ~8GB  | Fast     | Excellent | Best quality      |
| mistral    | 4.1GB | ~8GB  | Fast     | Very Good | Great alternative |
| phi        | 1.6GB | ~4GB  | Fastest  | Good      | Low resource      |
| codellama  | 3.8GB | ~8GB  | Fast     | Good      | Code-focused      |

**Advantages**:
- ✅ Free - no API costs
- ✅ Private - data stays on your machine
- ✅ No API key needed
- ✅ Works offline

**Setup**:
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2

# Run the app (Ollama will start automatically)
streamlit run app.py
```

#### OpenAI Models (Optional)

| Model            | Cost/1K tokens | Speed  | Quality   | Use Case         |
|------------------|----------------|--------|-----------|------------------|
| gpt-3.5-turbo    | $0.0015        | Fast   | Good      | Cost-effective   |
| gpt-4-turbo      | $0.01          | Medium | Excellent | High quality     |
| gpt-4            | $0.03          | Slow   | Best      | Premium quality  |

**Setup**:
```bash
# Set in .env
AI_PROVIDER=openai
OPENAI_API_KEY=your-api-key-here
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

### Processing Modes

**Summarize Mode** - Get clear summaries of content:
- Perfect for YouTube videos, podcasts, or long recordings
- Extracts key points automatically
- Choose from concise, detailed, or bullet-point styles

**Refine Mode** - Transform your voice into professional messages:
- Record what you want to say naturally
- AI refines it into a clear, well-structured message
- Choose tone: professional, friendly, formal, or casual
- Optionally specify recipient context for better refinement

### Step-by-Step Guide

1. **Configure Settings** (in sidebar):
   - Select AI provider (Local LLM or OpenAI)
   - Choose your model
   - Enter your API key (only for OpenAI)
   - Select processing mode (Summarize or Refine)
   - Configure mode-specific options

2. **Choose Input Method**:

   **YouTube Transcription**:
   - Navigate to the "YouTube" tab
   - Paste a YouTube URL
   - Click "Get Transcript"
   - View transcript and AI-processed result

   **File Upload**:
   - Navigate to the "Upload File" tab
   - Upload an audio file (mp3, wav, m4a, ogg, flac)
   - Click "Transcribe File"
   - View transcript and AI-processed result

   **Voice Recording**:
   - Navigate to the "Record Audio" tab
   - Click the microphone button to start/stop recording
   - Click "Transcribe Recording"
   - View transcript and AI-processed result

3. **Download Results**:
   - Use the download buttons to save your transcript and AI-processed output

## 🔒 Privacy & Security

- **Local Transcription**: Audio is transcribed locally using Whisper (no data sent to external services)
- **No Data Storage**: Transcripts are not stored permanently
- **Temporary Files**: Automatically cleaned up after processing
- **API Key Security**: Store your OpenAI API key securely in `.env` (never commit to version control)

## 🚢 Deployment

### Docker Deployment (Recommended)

AiTranscript can be deployed using Docker for easy setup and portability. This is the **recommended method** for deploying with local LLM support.

**Quick Start**:
```bash
# Clone and navigate to the project
git clone <repository-url>
cd AiTranscript

# Start with Docker Compose
docker-compose up -d

# Access at http://localhost:8501
```

**Important**: See [`DEPLOYMENT.md`](DEPLOYMENT.md) for complete deployment instructions, including:
- Why Vercel is **not compatible** with local LLMs
- Recommended platforms (Railway, Render, DigitalOcean)
- Detailed Docker setup and configuration
- Environment variables and resource requirements
- Troubleshooting guide

### Alternative: Streamlit Cloud (OpenAI Only)

If you want to use Streamlit Cloud, you **must use OpenAI provider** (local LLM not supported):

1. Push your code to GitHub
2. Sign up for [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Add your `OPENAI_API_KEY` in the Secrets section
5. Set `AI_PROVIDER=openai` in Secrets
6. Deploy!

**Note**: This option requires an OpenAI API key and incurs API costs. For free, private AI processing, use Docker deployment with local LLM.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for local transcription
- [Ollama](https://ollama.ai/) for local LLM support
- [Streamlit](https://streamlit.io/) for the web framework
- [OpenAI](https://openai.com/) for GPT API

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

**Built with ❤️ using Streamlit, Whisper, Ollama, and OpenAI GPT**
