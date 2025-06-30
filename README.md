# Text-to-Image Generator

A Python FastAPI application that generates images from text prompts using Replicate's Stable Diffusion XL model, with both REST API and MCP (Model Context Protocol) server support.

## Features

- 🎨 **Text-to-Image Generation**: Create stunning images from text prompts
- 🌐 **REST API**: Full REST API for programmatic access
- 🤖 **MCP Server**: Model Context Protocol support for LLM integration
- 🖥️ **Web Interface**: Beautiful web UI for easy image generation
- 🐳 **Docker Support**: Easy deployment with Docker
- ☁️ **Cloud Ready**: Deploy to Railway, Heroku, or any cloud platform
- 📊 **Auto-generated Docs**: Interactive API documentation with Swagger UI

## Prerequisites

- Python 3.12+ installed
- Replicate API token (required for image generation)

## Quick Start

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd text-to-image
pip install -r requirements.txt
```

### 2. Set Environment Variables

Copy the example environment file and add your Replicate API token:

```bash
cp env.example .env
```

Edit `.env` and add your Replicate API token:
```
REPLICATE_API_TOKEN=your_replicate_token_here
```

Get your token from: https://replicate.com/account/api-tokens

### 3. Run the Application

**Development mode:**
```bash
uvicorn app.main:app --reload --port 3123
```

**Production mode:**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 3123
```

The server will start on `http://localhost:3123`

## MCP (Model Context Protocol) Server

The application includes a full MCP server for AI agent integration. This allows AI assistants like Claude Desktop to directly generate images through natural language commands.

### **Quick MCP Test**

```bash
# Test MCP server functionality
python3 test_mcp.py

# List available MCP tools
curl -X POST "http://localhost:3123/mcp/messages" \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'

# Generate image via MCP
curl -X POST "http://localhost:3123/mcp/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "generate-image",
      "arguments": {"prompt": "a beautiful sunset"}
    }
  }'
```

### **Available MCP Tools**

| Tool | Description | Input |
|------|-------------|-------|
| `generate-image` | Generate image from text prompt | `{"prompt": "description"}` |
| `get-image-status` | Check image generation status | `{"imageId": "id"}` |

### **Integration Examples**

- **Claude Desktop**: Add `http://localhost:3123` as MCP server
- **n8n Workflows**: Use HTTP Request nodes to call MCP endpoints
- **Python Scripts**: Use the provided `examples/mcp_client.py`
- **JavaScript**: Use the provided `examples/mcp_client.js`

### **MCP Server Endpoints**

- **`GET /mcp/sse`** - Server-Sent Events for real-time communication
- **`POST /mcp/messages`** - Main MCP messages endpoint

### **Testing MCP Functionality**

```bash
# Run comprehensive MCP tests
python3 test_mcp.py

# Test individual endpoints
python3 examples/mcp_client.py
```

## Docker Deployment

### Using Docker Compose (Recommended)

The easiest way to run the application is using Docker Compose:

```bash
# Build and start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Using Docker Directly

```bash
# Build the image
docker build -f main.Dockerfile -t text-to-image .

# Run the container
docker run -p 3123:3123 --env-file .env text-to-image
```

### Using Tiny Alpine Image

For minimal resource usage:

```bash
# Build tiny image
docker build -f main-tiny.Dockerfile -t text-to-image-tiny .

# Run with docker-compose
docker-compose --profile tiny up -d
```

### Docker Configuration Options

| Dockerfile | Base Image | Size | Use Case |
|------------|------------|------|----------|
| `main.Dockerfile` | `python:3.12-slim` | ~200MB | Production |
| `main-tiny.Dockerfile` | `python:3.12-alpine` | ~150MB | Resource-constrained |
| `main-cuda.Dockerfile` | `nvidia/cuda:12.1-devel-ubuntu22.04` | ~2GB | GPU acceleration |

### Docker Compose Profiles

```bash
# Production
docker-compose up -d

# Tiny version
docker-compose --profile tiny up -d

# CUDA version
docker-compose --profile cuda up -d

# Development with hot reload
docker-compose --profile dev up -d
```

## Cloud Deployment

### Railway Deployment

1. **Connect to Railway:**
   - Go to [Railway.app](https://railway.app)
   - Connect your GitHub repository

2. **Set Environment Variables:**
   - Add `REPLICATE_API_TOKEN` with your token
   - Railway will automatically set `PORT`

3. **Deploy:**
   - Railway will automatically build and deploy your application

### VPS Deployment

For VPS deployment (Ubuntu ≥ 22.04, ≥ 4GB RAM, ≥ 2vCPUs):

#### Using PM2 (Recommended)

```bash
# Install PM2
npm install -g pm2

# Set environment variables in ~/.bashrc
echo 'export REPLICATE_API_TOKEN="your_token_here"' >> ~/.bashrc
echo 'export PORT=3123' >> ~/.bashrc
source ~/.bashrc

# Start with PM2
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save
pm2 startup
```

#### Using Docker on VPS

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Run the application
docker run -d \
  --name text-to-image \
  -p 3123:3123 \
  --env-file .env \
  --restart unless-stopped \
  text-to-image
```

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `REPLICATE_API_TOKEN` | Your Replicate API token | Yes | None |
| `PORT` | Server port | No | 3123 |
| `PYTHONPATH` | Python path | No | /app |

## Usage

### Web Interface

Visit `http://localhost:3123` to use the web interface for generating images.

### API Documentation

Visit `http://localhost:3123/docs` for interactive API documentation (Swagger UI).

### REST API

#### Generate Image
```bash
curl -X POST "http://localhost:3123/api/generate-image" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "a beautiful sunset over mountains"}'
```

Response:
```json
{
  "imageId": "abc123def456",
  "imageUrl": "https://replicate.delivery/pbxt/...",
  "status": "ready",
  "message": "Image generated successfully"
}
```

#### Get Image Status
```bash
curl "http://localhost:3123/api/image/abc123def456/status"
```

#### List All Images
```bash
curl "http://localhost:3123/api/images"
```

#### Delete Image
```bash
curl -X DELETE "http://localhost:3123/api/image/abc123def456"
```

## API Endpoints

### REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/generate-image` | Generate image from prompt |
| GET | `/api/image/{id}/status` | Get image status |
| GET | `/api/images` | List all images |
| DELETE | `/api/image/{id}` | Delete image |
| GET | `/docs` | Interactive API documentation |

### MCP Server

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/mcp/sse` | Server-Sent Events endpoint |
| POST | `/mcp/messages` | MCP messages endpoint |

## Testing

### Test MCP Server

```bash
# Run comprehensive MCP tests
python3 test_mcp.py

# Test individual endpoints
python3 examples/mcp_client.py
```

### Test REST API

```bash
# Health check
curl http://localhost:3123/health

# Generate test image
curl -X POST "http://localhost:3123/api/generate-image" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test image"}'
```

## Troubleshooting

### Docker Issues

**Memory Requirements:**
- The server needs at least 1GB free memory
- For Docker Desktop, allocate at least 2GB RAM

**WSL2 on Windows:**
- Set resource limits in WSL2: `wsl --set-version Ubuntu 2`
- Or configure in Docker Desktop settings

**Common Docker Commands:**
```bash
# Check container logs
docker logs <container_name>

# Access container shell
docker exec -it <container_name> /bin/bash

# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Common Issues

1. **"REPLICATE_API_TOKEN not found"**
   - Make sure you've set the environment variable
   - Check that your `.env` file exists and is properly formatted

2. **"No image generated"**
   - Verify your Replicate token is valid
   - Check that you have sufficient credits in your Replicate account

3. **Port already in use**
   - Change the PORT environment variable
   - Or kill the process using the port

4. **Import errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`

5. **Docker build fails**
   - Check Docker has enough disk space
   - Clear Docker cache: `docker system prune -a`

6. **MCP server not responding**
   - Check if server is running: `curl http://localhost:3123/health`
   - Verify MCP endpoints: `python3 test_mcp.py`

### Debug Mode

Run with debug logging:
```bash
# Local development
uvicorn app.main:app --reload --log-level debug

# Docker
docker run -p 3123:3123 --env-file .env text-to-image python -m uvicorn app.main:app --host 0.0.0.0 --port 3123 --log-level debug
```

## Development

### Project Structure

```
text-to-image/
├── app/
│   └── main.py            # Main FastAPI application
├── static/
│   └── index.html         # Web interface
├── examples/
│   ├── mcp_client.py      # Python MCP client
│   └── mcp_client.js      # JavaScript MCP client
├── requirements.txt       # Python dependencies
├── main.Dockerfile        # Main Docker configuration
├── main-tiny.Dockerfile   # Tiny Alpine Docker configuration
├── main-cuda.Dockerfile   # CUDA Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── ecosystem.config.js    # PM2 configuration
├── .dockerignore         # Docker ignore file
├── test_mcp.py           # MCP server test script
├── env.example           # Environment variables example
└── README.md            # This file
```

### Adding New Features

1. **New API Endpoints**: Add routes in `app/main.py`
2. **New MCP Tools**: Add tools in the `/mcp/messages` handler
3. **UI Improvements**: Modify `static/index.html`
4. **New Dependencies**: Add to `requirements.txt`

### Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run in development mode
uvicorn app.main:app --reload

# Run with Docker Compose
docker-compose up --build

# Test MCP functionality
python3 test_mcp.py

# Run examples
python3 examples/mcp_client.py

# Run tests (if you add them)
pytest

# Format code
black app/

# Lint code
flake8 app/
```

## License

This project is licensed under the MIT License.

## Acknowledgments

- ❤️ [Replicate](https://replicate.com) for Stable Diffusion XL
- ❤️ [FastAPI](https://fastapi.tiangolo.com) for the web framework
- ❤️ [Model Context Protocol](https://modelcontextprotocol.io) for LLM integration
- ❤️ [short-video-maker](https://github.com/gyoridavid/short-video-maker) for deployment patterns

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs for error messages
3. Ensure all environment variables are set correctly
4. Verify your Replicate token is valid
5. Test MCP functionality with `python3 test_mcp.py` 