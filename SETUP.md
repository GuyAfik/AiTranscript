# 🚀 AiTranscript Setup Guide

This guide will walk you through setting up and running AiTranscript on your local machine.

## Prerequisites Checklist

Before you begin, ensure you have:

- [ ] Python 3.11 or higher installed
- [ ] FFmpeg installed on your system
- [ ] OpenAI API key (get one at https://platform.openai.com/api-keys)
- [ ] Internet connection for downloading dependencies

## Step-by-Step Setup

### 1. Install FFmpeg

FFmpeg is required for audio processing.

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Windows:**
1. Download from https://ffmpeg.org/download.html
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add `C:\ffmpeg\bin` to your system PATH

**Verify installation:**
```bash
ffmpeg -version
```

### 2. Install uv Package Manager

uv is a fast Python package manager that we use for dependency management.

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Verify installation:**
```bash
uv --version
```

### 3. Clone and Setup Project

```bash
# Clone the repository
git clone <repository-url>
cd AiTranscript

# Create virtual environment
uv venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install all dependencies
uv pip install -e .
```

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your favorite editor
# On macOS/Linux:
nano .env
# On Windows:
notepad .env
```

**Required configuration in `.env`:**
```bash
# Your OpenAI API key (REQUIRED for AI features)
OPENAI_API_KEY=sk-your-actual-api-key-here

# Whisper model size (optional, default: base)
# Options: tiny, base, small, medium, large
WHISPER_MODEL_SIZE=base

# OpenAI model (optional, default: gpt-4-turbo-preview)
OPENAI_MODEL=gpt-4-turbo-preview
```

### 5. Run the Application

```bash
streamlit run app.py
```

The application will automatically open in your default browser at `http://localhost:8501`.

## Testing the Application

### Test 1: YouTube Transcription

1. Go to the "YouTube" tab
2. Paste a YouTube URL (e.g., `https://www.youtube.com/watch?v=dQw4w9WgXcQ`)
3. Click "Get Transcript"
4. Verify that:
   - Transcript is extracted successfully
   - AI summary is generated (if API key is configured)
   - Key points are displayed

### Test 2: File Upload

1. Go to the "Upload File" tab
2. Upload a test audio file (mp3, wav, m4a, ogg, or flac)
3. Click "Transcribe File"
4. Verify that:
   - File is uploaded successfully
   - Audio player shows the file
   - Transcription completes
   - AI summary is generated

### Test 3: Voice Recording

1. Go to the "Record Audio" tab
2. Click the microphone button to start recording
3. Speak for a few seconds
4. Click the microphone button again to stop
5. Click "Transcribe Recording"
6. Verify that:
   - Recording is captured
   - Audio playback works
   - Transcription completes
   - AI summary is generated

## Troubleshooting

### Issue: "FFmpeg not found"

**Solution:**
- Ensure FFmpeg is installed and in your system PATH
- Restart your terminal after installation
- Verify with `ffmpeg -version`

### Issue: "OpenAI API error"

**Solution:**
- Check that your API key is correct in `.env`
- Verify you have credits in your OpenAI account
- Check your internet connection

### Issue: "Module not found" errors

**Solution:**
```bash
# Reinstall dependencies
uv pip install -e .

# Or install specific missing package
uv pip install package-name
```

### Issue: Whisper model download is slow

**Solution:**
- The first time you run transcription, Whisper will download the model
- This is a one-time download and will be cached
- Use a smaller model (tiny or base) for faster initial setup

### Issue: "Permission denied" for microphone

**Solution:**
- Grant microphone permissions in your browser
- Check system microphone settings
- Try a different browser if issues persist

## Performance Tips

### For Faster Transcription:
- Use smaller Whisper models (tiny or base)
- Use GPU if available (set `WHISPER_DEVICE=cuda` in `.env`)

### For Better Accuracy:
- Use larger Whisper models (small, medium, or large)
- Ensure good audio quality
- Minimize background noise

### For Cost Optimization:
- Use local Whisper for transcription (free)
- Use gpt-3.5-turbo for summaries (cheaper)
- Only enable AI features when needed

## Next Steps

Once setup is complete:

1. **Customize Settings**: Adjust Whisper model size and OpenAI model in `.env`
2. **Explore Features**: Try all three input methods
3. **Read Documentation**: Check `README.md` for detailed usage
4. **Review Architecture**: See `plans/architecture.md` for technical details

## Getting Help

If you encounter issues:

1. Check this troubleshooting guide
2. Review the logs in the terminal
3. Open an issue on GitHub with:
   - Error message
   - Steps to reproduce
   - Your environment (OS, Python version)

---

**Happy Transcribing! 🎙️**
