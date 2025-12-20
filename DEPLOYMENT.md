# Deployment Guide

## Overview

AiTranscript can be deployed using Docker containers. This guide covers deployment options and instructions.

## ⚠️ Important: Vercel Limitations

**Vercel is NOT compatible with this application when using local LLMs (Ollama)** because:

1. **Serverless Architecture**: Vercel uses serverless functions that spin up and down on demand. Ollama requires a persistent process to run the LLM models.
2. **No Docker Support**: Vercel doesn't support Docker containers in their standard deployment.
3. **Resource Constraints**: Running LLMs requires significant memory and CPU, which exceeds Vercel's serverless function limits.
4. **Persistent Storage**: Ollama models need to be downloaded and stored (several GB), which isn't suitable for Vercel's ephemeral filesystem.

### Alternative for Vercel

If you **must** use Vercel, you can:
- Deploy with **OpenAI provider only** (remove Ollama dependency)
- Modify the application to use only cloud-based AI services
- This defeats the purpose of having a free, local LLM option

## Recommended Deployment Platforms

For deploying with local LLM support (Ollama), use these platforms:

### 1. **Railway** (Recommended - Easiest)
- ✅ Docker support
- ✅ Free tier available
- ✅ Simple deployment from GitHub
- ✅ Automatic HTTPS
- 📝 [Railway.app](https://railway.app)

**Steps:**
1. Push your code to GitHub
2. Connect Railway to your repository
3. Railway will auto-detect the Dockerfile
4. Set environment variables in Railway dashboard
5. Deploy!

### 2. **Render**
- ✅ Docker support
- ✅ Free tier available
- ✅ Easy setup
- 📝 [Render.com](https://render.com)

**Steps:**
1. Create a new Web Service
2. Connect your GitHub repository
3. Select "Docker" as environment
4. Configure environment variables
5. Deploy

### 3. **DigitalOcean App Platform**
- ✅ Docker support
- ✅ $5/month starter tier
- ✅ Reliable infrastructure
- 📝 [DigitalOcean Apps](https://www.digitalocean.com/products/app-platform)

### 4. **Self-Hosted (VPS)**
- ✅ Full control
- ✅ Best performance
- ✅ Most cost-effective for heavy usage
- Platforms: DigitalOcean Droplets, Linode, Vultr, AWS EC2

## Docker Deployment

### Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)

### Quick Start with Docker Compose

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd AiTranscript
```

2. **Create environment file**
```bash
cp .env.example .env
```

3. **Edit `.env` file** (optional - only needed for OpenAI)
```bash
# For OpenAI support (optional)
OPENAI_API_KEY=your_openai_api_key_here
```

4. **Build and run**
```bash
docker-compose up -d
```

5. **Access the application**
- Open browser to: `http://localhost:8501`
- Ollama API available at: `http://localhost:11434`

6. **View logs**
```bash
docker-compose logs -f
```

7. **Stop the application**
```bash
docker-compose down
```

### Manual Docker Build

If you prefer to build manually:

```bash
# Build the image
docker build -t aitranscript .

# Run the container
docker run -d \
  -p 8501:8501 \
  -p 11434:11434 \
  -v ollama_models:/root/.ollama \
  --name aitranscript \
  aitranscript
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | No | - | OpenAI API key (only if using OpenAI provider) |
| `DEFAULT_AI_PROVIDER` | No | `local` | Default AI provider (`local` or `openai`) |
| `DEFAULT_AI_MODEL` | No | `llama2` | Default model for local LLM |

## Resource Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB (8GB recommended for larger models)
- **Storage**: 10GB (for Ollama models)
- **Network**: Stable internet for initial model download

### Recommended for Production
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 20GB+
- **GPU**: Optional but significantly improves performance

## First-Time Setup

When you first run the application:

1. **Ollama will start** and be ready to accept requests
2. **First model download**: When you first use the AI features, Ollama will download the selected model (e.g., llama2 ~4GB)
3. **Subsequent uses**: Models are cached and load instantly

## Updating the Application

### With Docker Compose
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose up -d --build
```

### Manual Docker
```bash
# Stop and remove old container
docker stop aitranscript
docker rm aitranscript

# Rebuild image
docker build -t aitranscript .

# Run new container
docker run -d -p 8501:8501 -p 11434:11434 -v ollama_models:/root/.ollama --name aitranscript aitranscript
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs

# Or for manual Docker
docker logs aitranscript
```

### Ollama model download fails
- Ensure you have enough disk space
- Check internet connection
- Try a smaller model first (e.g., `llama2:7b` instead of `llama2:13b`)

### Out of memory errors
- Increase Docker memory limit in Docker Desktop settings
- Use a smaller model
- Upgrade your hosting plan

### Port already in use
```bash
# Check what's using the port
lsof -i :8501

# Change port in docker-compose.yml
ports:
  - "8502:8501"  # Use 8502 instead
```

## Production Considerations

1. **HTTPS**: Use a reverse proxy (nginx, Caddy) or platform-provided HTTPS
2. **Backups**: Regularly backup the `ollama_models` volume
3. **Monitoring**: Set up health checks and monitoring
4. **Scaling**: For high traffic, consider multiple instances with load balancing
5. **Security**: 
   - Don't expose Ollama port (11434) publicly
   - Use environment variables for secrets
   - Keep Docker images updated

## Cost Comparison

| Platform | Free Tier | Paid Tier | Notes |
|----------|-----------|-----------|-------|
| Railway | 500 hours/month | $5-20/month | Best for hobby projects |
| Render | 750 hours/month | $7-25/month | Good free tier |
| DigitalOcean | - | $5-12/month | Reliable, predictable pricing |
| Self-hosted VPS | - | $5-10/month | Most control, best value |
| Vercel | ❌ Not compatible | ❌ Not compatible | Cannot run Ollama |

## Support

For deployment issues:
1. Check the logs first
2. Review this documentation
3. Open an issue on GitHub with:
   - Platform you're deploying to
   - Error messages from logs
   - Steps you've tried

## Next Steps

After successful deployment:
1. Test the application with a sample audio file
2. Try both processing modes (Summarize and Refine)
3. Experiment with different AI models
4. Configure your preferred settings