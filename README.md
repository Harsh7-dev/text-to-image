# Text-to-Video API

A FastAPI service that generates videos from text prompts using Hugging Face's text-to-video models.

## Prerequisites

- Docker installed
- Hugging Face API token (optional, for higher rate limits)

## Setup

1. **Get your Hugging Face API token (optional):**
   - Go to: https://huggingface.co/settings/tokens
   - Create a new API token
   - Copy the token

2. **Configure your API token:**
   - Edit the `.env` file in the project root
   - Add your Hugging Face API token:
   ```
   HUGGINGFACE_API_TOKEN=your_token_here
   ```
   - Note: The app works without a token but with limited requests

3. **Build and run with Docker:**
   ```bash
   # Build the Docker image
   docker build -t text-to-video .
   
   # Run the container
   docker run -p 8000:8000 text-to-video
   ```

## Usage

The API will be available at `http://localhost:8000`

### Web Interface

Visit `http://localhost:8000` to use the beautiful web interface for generating videos.

### API Endpoints

- **Health Check:** `GET /health`
- **Generate Video:** `POST /generate`

### Example Request

```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{"text": "a beautiful sunset over mountains"}'
```

### Response

```json
{
  "video_path": "output/generated_video.mp4",
  "message": "Video generated successfully"
}
```

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Output

Generated videos are saved in the `./output` directory inside the container.

## Environment Variables

The application reads environment variables from the `.env` file:
- `HUGGINGFACE_API_TOKEN`: Your Hugging Face API token (optional)

## Model Used

This API uses **Text-to-Video models** from Hugging Face, which generate short video clips from text descriptions.

## Security Notes

- The container runs as a non-root user for security
- Health checks are included for monitoring
- Environment variables are loaded from `.env` file
- API tokens are not exposed in command line arguments

## Deployment

### Railway Deployment

This application is configured for easy deployment on Railway. See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

Quick deployment steps:
1. Push your code to GitHub
2. Connect your repository to Railway
3. Set the `HUGGINGFACE_API_TOKEN` environment variable in Railway (optional)
4. Deploy!

### Other Platforms

The Dockerfile is compatible with other platforms like:
- Heroku
- Google Cloud Run
- AWS ECS
- DigitalOcean App Platform

## Troubleshooting

- **Port already in use**: The service runs on port 8000 by default. If you need a different port, modify the Docker run command: `docker run -p 8001:8000 text-to-video`
- **API token errors**: Make sure your Hugging Face API token is valid and properly set in the `.env` file
- **Model access**: The app uses free models from Hugging Face, so no special access is required
- **Rate limits**: Without an API token, you're limited to a few requests per hour

## Project Structure

```
Text-to-Video/
├── app/
│   ├── main.py          # FastAPI application
│   └── static/
│       └── index.html   # Web interface
├── output/              # Generated videos (created by container)
├── .env                 # Environment variables (create this file)
├── Dockerfile           # Docker configuration
├── railway.json         # Railway deployment config
├── requirements.txt     # Python dependencies
├── DEPLOYMENT.md        # Deployment guide
└── README.md           # This file
```

## Development

To run the application locally without Docker:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your `.env` file with your Hugging Face API token (optional)

3. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Features

- 🎬 Beautiful, responsive web interface
- 🚀 Fast video generation with Hugging Face models
- 📱 Mobile-friendly design
- 🔒 Secure token handling
- 🐳 Docker containerization
- ☁️ Railway deployment ready
- 💾 Video download functionality
- 🎯 Example prompts for inspiration 