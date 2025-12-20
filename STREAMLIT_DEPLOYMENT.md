# Streamlit Share Deployment Guide

## ⚠️ Important Limitations

**Streamlit Share does NOT support local LLMs (Ollama)**. When deploying to Streamlit Share, you **MUST use OpenAI** as your AI provider.

### Why Ollama Won't Work on Streamlit Share:
1. **No persistent processes**: Streamlit Share can't run background services like Ollama
2. **Resource constraints**: Limited CPU/RAM, insufficient for running LLM models
3. **No custom Docker**: Can't install Ollama or download model files
4. **Ephemeral storage**: Models would need to be re-downloaded on every restart (several GB)

## 📋 Prerequisites

Before deploying to Streamlit Share, you need:

1. **GitHub Account**: Your code must be in a GitHub repository
2. **OpenAI API Key**: Required for AI processing (get one at [platform.openai.com](https://platform.openai.com/api-keys))
3. **Streamlit Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)

## 🚀 Deployment Steps

### Step 1: Prepare Your Repository

Your repository should have these files (already created):
- ✅ `app.py` - Main application
- ✅ `requirements.txt` - Python dependencies
- ✅ `packages.txt` - System packages (FFmpeg)
- ✅ `.streamlit/config.toml` - Streamlit configuration

### Step 2: Push to GitHub

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Ready for Streamlit Share deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy on Streamlit Share

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Select your repository, branch (main), and main file path (`app.py`)
4. Click **"Advanced settings"**

### Step 4: Configure Secrets

In the Advanced settings, add your secrets in TOML format:

```toml
# Required: OpenAI API Key
OPENAI_API_KEY = "sk-your-openai-api-key-here"

# Optional: Default settings
AI_PROVIDER = "openai"
OPENAI_MODEL = "gpt-4-turbo-preview"
WHISPER_MODEL_SIZE = "base"
```

### Step 5: Deploy

1. Click **"Deploy!"**
2. Wait 2-5 minutes for deployment
3. Your app will be live at: `https://YOUR_USERNAME-YOUR_REPO-RANDOM.streamlit.app`

## 🔧 Configuration

### Environment Variables (Secrets)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ Yes | - | Your OpenAI API key |
| `AI_PROVIDER` | No | `openai` | Must be "openai" for Streamlit Share |
| `OPENAI_MODEL` | No | `gpt-4-turbo-preview` | OpenAI model to use |
| `WHISPER_MODEL_SIZE` | No | `base` | Whisper model size (tiny/base/small) |

### Recommended Settings for Streamlit Share

Due to resource constraints, use these settings:

```toml
WHISPER_MODEL_SIZE = "base"  # or "tiny" for faster processing
OPENAI_MODEL = "gpt-3.5-turbo"  # cheaper and faster than GPT-4
```

## 💰 Cost Considerations

Since Streamlit Share requires OpenAI, you'll incur API costs:

### OpenAI Pricing (as of 2024)
- **GPT-3.5-turbo**: ~$0.0015 per 1K tokens (cheaper)
- **GPT-4-turbo**: ~$0.01 per 1K tokens (better quality)
- **GPT-4**: ~$0.03 per 1K tokens (best quality)

### Typical Usage Costs
- **Short transcript** (5 min audio): ~$0.01-0.05
- **Medium transcript** (30 min audio): ~$0.05-0.20
- **Long transcript** (1 hour audio): ~$0.10-0.40

**Tip**: Start with `gpt-3.5-turbo` to minimize costs while testing.

## 🔄 Updating Your App

To update your deployed app:

```bash
# Make your changes
git add .
git commit -m "Update description"
git push

# Streamlit Share will automatically redeploy
```

## 🐛 Troubleshooting

### App Won't Start

**Check logs**:
1. Go to your app on Streamlit Share
2. Click "Manage app" → "Logs"
3. Look for error messages

**Common issues**:
- Missing `OPENAI_API_KEY` in secrets
- Invalid API key
- Missing dependencies in `requirements.txt`

### "Module not found" Error

Make sure all dependencies are in [`requirements.txt`](requirements.txt:1):
```bash
# Locally test if all dependencies are correct
pip install -r requirements.txt
streamlit run app.py
```

### FFmpeg Not Found

Ensure [`packages.txt`](packages.txt:1) contains:
```
ffmpeg
```

### Out of Memory

Streamlit Share has limited resources. Solutions:
1. Use smaller Whisper model: `WHISPER_MODEL_SIZE = "tiny"`
2. Limit file upload size in the app
3. Consider upgrading to Streamlit Cloud (paid tier)

### API Rate Limits

If you hit OpenAI rate limits:
1. Reduce usage frequency
2. Upgrade your OpenAI plan
3. Add error handling in the app

## 📊 Resource Limits

Streamlit Share free tier limits:
- **CPU**: 1 core
- **RAM**: 1GB
- **Storage**: 1GB
- **Bandwidth**: Limited
- **Apps**: 3 public apps

For higher limits, consider:
- **Streamlit Cloud** (paid): More resources, private apps
- **Railway/Render**: Docker support with local LLM

## 🔒 Security Best Practices

1. **Never commit API keys** to GitHub
2. **Use Streamlit Secrets** for sensitive data
3. **Add `.env` to `.gitignore`** (already done)
4. **Rotate API keys** periodically
5. **Monitor API usage** on OpenAI dashboard

## 🆚 Streamlit Share vs Docker Deployment

| Feature | Streamlit Share | Docker (Railway/Render) |
|---------|----------------|------------------------|
| **Setup** | Very Easy | Medium |
| **Cost** | Free + OpenAI API | $5-20/month (free tier available) |
| **Local LLM** | ❌ No | ✅ Yes |
| **Privacy** | Data sent to OpenAI | ✅ Data stays local (with Ollama) |
| **Resources** | Limited (1GB RAM) | Configurable (4-8GB+) |
| **Best For** | Quick demos, testing | Production, privacy-focused |

## 📝 Deployment Checklist

Before deploying, ensure:

- [ ] Code is pushed to GitHub
- [ ] `requirements.txt` is up to date
- [ ] `packages.txt` includes `ffmpeg`
- [ ] `.streamlit/config.toml` exists
- [ ] You have an OpenAI API key
- [ ] `.env` is in `.gitignore`
- [ ] App works locally with OpenAI provider

## 🎯 Next Steps After Deployment

1. **Test your app** with sample audio files
2. **Monitor costs** on OpenAI dashboard
3. **Share your app** URL with users
4. **Set up monitoring** for errors
5. **Consider upgrading** if you need:
   - Private apps
   - More resources
   - Local LLM support (switch to Docker deployment)

## 🆘 Getting Help

If you encounter issues:

1. **Check Streamlit Logs**: In app management dashboard
2. **Review OpenAI Status**: [status.openai.com](https://status.openai.com)
3. **Streamlit Community**: [discuss.streamlit.io](https://discuss.streamlit.io)
4. **GitHub Issues**: Open an issue in your repository

## 🔄 Alternative: Docker Deployment

If you want to use **local LLM (Ollama)** for free AI processing:

1. See [`DEPLOYMENT.md`](DEPLOYMENT.md) for Docker deployment
2. Deploy to Railway, Render, or DigitalOcean
3. Enjoy free, private AI processing without API costs

**Recommended for**:
- Privacy-focused applications
- High-volume usage (avoid API costs)
- Full control over AI models
