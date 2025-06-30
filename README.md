# Text-to-Image API

A FastAPI service that generates images from text prompts using Replicate's Stable Diffusion XL model.

## Prerequisites

- Docker installed
- Replicate API token (required for image generation)

## Setup

1. **Get your Replicate API token:**
   - Go to: https://replicate.com/account/api-tokens
   - Create a new API token
   - Copy the token

2. **Configure your API token:**
   - Edit the `.env` file in the project root
   - Add your Replicate API token:
   ```
   REPLICATE_API_TOKEN=your_token_here
   ```

3. **Build and run with Docker:**
   ```bash
   # Build the Docker image
   docker build -t text-to-image .
   
   # Run the container
   docker run -p 8000:8000 --env-file .env text-to-image
   ```

## Usage

The API will be available at `http://localhost:8000`

### Web Interface

Visit `http://localhost:8000` to use the beautiful web interface for generating images.

### API Endpoints

- **Health Check:** `GET /health`
- **Generate Image:** `POST /generate`
- **API Info:** `GET /info`

### Example Request

```bash
curl -X POST "http://localhost:8000/generate" \
     -H "Content-Type: application/json" \
     -d '{"text": "a beautiful sunset over mountains"}'
```

### Response

```json
{
  "image_path": "output/generated_image.png",
  "image_url": "https://replicate.delivery/pbxt/...",
  "message": "Image generated successfully"
}
```

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Output

Generated images are saved in the `./output` directory inside the container.

## Environment Variables

The application reads environment variables from the `.env` file:
- `REPLICATE_API_TOKEN`: Your Replicate API token (required)

## Model Used

This API uses **Stable Diffusion XL** from Replicate, which generates high-quality images from text descriptions.

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
3. Set the `REPLICATE_API_TOKEN` environment variable in Railway
4. Deploy!

### Other Platforms

The Dockerfile is compatible with other platforms like:
- Heroku
- Google Cloud Run
- AWS ECS
- DigitalOcean App Platform

## Troubleshooting

- **Port already in use**: The service runs on port 8000 by default. If you need a different port, modify the Docker run command: `docker run -p 8001:8000 --env-file .env text-to-image`
- **API token errors**: Make sure your Replicate API token is valid and properly set in the `.env` file
- **Billing issues**: Replicate requires a payment method for image generation. Check your billing status at https://replicate.com/account/billing
- **Rate limits**: Replicate has rate limits based on your plan

## Project Structure

```
Text-to-Image/
├── app/
│   ├── main.py          # FastAPI application
│   └── static/
│       └── index.html   # Web interface
├── output/              # Generated images (created by container)
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

2. Set up your `.env` file with your Replicate API token

3. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Features

- 🎨 Beautiful, responsive web interface
- 🚀 Fast image generation with Stable Diffusion XL
- 📱 Mobile-friendly design
- 🔒 Secure token handling
- 🐳 Docker containerization
- ☁️ Railway deployment ready
- 💾 Image download functionality
- 🎯 High-quality image generation
- 🔄 Latest Python 3.12 and FastAPI 0.109.2 