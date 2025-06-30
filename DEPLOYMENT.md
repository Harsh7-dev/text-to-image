# Deployment Guide

This guide covers all deployment options for the Text-to-Image Generator, following the patterns from [short-video-maker](https://github.com/gyoridavid/short-video-maker).

## 🚀 Quick Deployment Options

### **Option 1: Railway (Recommended for Cloud)**

1. **Fork/Clone Repository**
   ```bash
   git clone https://github.com/your-username/text-to-image.git
   cd text-to-image
   ```

2. **Connect to Railway**
   - Go to [Railway.app](https://railway.app)
   - Connect your GitHub repository
   - Railway will automatically detect the `railway.json` configuration

3. **Set Environment Variables**
   - Add `REPLICATE_API_TOKEN` with your token
   - Railway will automatically set `PORT`

4. **Deploy**
   - Railway will automatically build and deploy
   - Your app will be available at `https://your-app.railway.app`

### **Option 2: Docker Compose (Local/Server)**

```bash
# Clone repository
git clone https://github.com/your-username/text-to-image.git
cd text-to-image

# Set environment variables
cp env.example .env
# Edit .env and add your REPLICATE_API_TOKEN

# Deploy with Docker Compose
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

### **Option 3: VPS with PM2**

```bash
# Install dependencies
sudo apt update
sudo apt install -y python3.12 python3-pip curl git

# Clone repository
git clone https://github.com/your-username/text-to-image.git
cd text-to-image

# Install Python dependencies
pip3 install -r requirements.txt

# Install PM2
npm install -g pm2

# Set environment variables
echo 'export REPLICATE_API_TOKEN="your_token_here"' >> ~/.bashrc
echo 'export PORT=3123' >> ~/.bashrc
source ~/.bashrc

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

## 🐳 Docker Deployment Options

### **Standard Production Build**

```bash
# Build and run
docker build -f main.Dockerfile -t text-to-image .
docker run -d -p 3123:3123 --env-file .env --name text-to-image text-to-image
```

### **Tiny Alpine Build (Resource-Constrained)**

```bash
# Build and run tiny version
docker build -f main-tiny.Dockerfile -t text-to-image-tiny .
docker run -d -p 3124:3123 --env-file .env --name text-to-image-tiny text-to-image-tiny
```

### **CUDA Build (GPU Acceleration)**

```bash
# Build and run with CUDA support
docker build -f main-cuda.Dockerfile -t text-to-image-cuda .
docker run -d -p 3125:3123 --env-file .env --gpus all --name text-to-image-cuda text-to-image-cuda
```

### **Docker Compose Profiles**

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

## ☁️ Cloud Platform Deployment

### **Railway**

**Automatic Deployment:**
- Connect GitHub repository to Railway
- Railway uses `railway.json` for configuration
- Automatic deployment on git push

**Manual Deployment:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### **Heroku**

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Create app
heroku create your-text-to-image-app

# Set environment variables
heroku config:set REPLICATE_API_TOKEN=your_token_here

# Deploy
git push heroku main
```

### **DigitalOcean App Platform**

1. **Create App**
   - Go to DigitalOcean App Platform
   - Connect GitHub repository
   - Select Python as runtime

2. **Configure Environment**
   - Set `REPLICATE_API_TOKEN`
   - Set build command: `pip install -r requirements.txt`
   - Set run command: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Deploy**
   - Click "Create Resources"

### **Google Cloud Run**

```bash
# Build and push to Google Container Registry
docker build -f main.Dockerfile -t gcr.io/your-project/text-to-image .
docker push gcr.io/your-project/text-to-image

# Deploy to Cloud Run
gcloud run deploy text-to-image \
  --image gcr.io/your-project/text-to-image \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars REPLICATE_API_TOKEN=your_token_here
```

### **AWS ECS**

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com
docker build -f main.Dockerfile -t text-to-image .
docker tag text-to-image:latest your-account.dkr.ecr.us-east-1.amazonaws.com/text-to-image:latest
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/text-to-image:latest

# Deploy to ECS (requires ECS task definition and service)
```

## 🖥️ VPS Deployment

### **Ubuntu 22.04+ VPS**

**System Requirements:**
- Ubuntu ≥ 22.04
- ≥ 4GB RAM
- ≥ 2vCPUs
- ≥ 5GB storage

**Installation Steps:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.12 python3-pip curl git nginx

# Clone repository
git clone https://github.com/your-username/text-to-image.git
cd text-to-image

# Install Python dependencies
pip3 install -r requirements.txt

# Install PM2
npm install -g pm2

# Set environment variables
echo 'export REPLICATE_API_TOKEN="your_token_here"' >> ~/.bashrc
echo 'export PORT=3123' >> ~/.bashrc
source ~/.bashrc

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup

# Configure Nginx (optional)
sudo nano /etc/nginx/sites-available/text-to-image
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3123;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/text-to-image /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### **Docker on VPS**

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Clone and run
git clone https://github.com/your-username/text-to-image.git
cd text-to-image

# Create .env file
cp env.example .env
# Edit .env and add your token

# Run with Docker
docker run -d \
  --name text-to-image \
  -p 3123:3123 \
  --env-file .env \
  --restart unless-stopped \
  text-to-image
```

## 🔧 Environment Configuration

### **Required Environment Variables**

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `REPLICATE_API_TOKEN` | Your Replicate API token | Yes | None |
| `PORT` | Server port | No | 3123 |
| `PYTHONPATH` | Python path | No | /app |

### **Optional Environment Variables**

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging level | INFO |
| `CORS_ORIGINS` | CORS allowed origins | * |
| `MAX_WORKERS` | Maximum workers | 1 |

### **Setting Environment Variables**

**Local Development:**
```bash
cp env.example .env
# Edit .env file
```

**Docker:**
```bash
docker run -e REPLICATE_API_TOKEN=your_token -p 3123:3123 text-to-image
```

**Docker Compose:**
```yaml
environment:
  - REPLICATE_API_TOKEN=${REPLICATE_API_TOKEN}
```

**Cloud Platforms:**
- Railway: Use dashboard or `railway variables set`
- Heroku: `heroku config:set`
- DigitalOcean: Use App Platform dashboard

## 🔍 Monitoring and Health Checks

### **Health Check Endpoint**

```bash
# Check if service is running
curl http://your-domain.com/health

# Expected response
{"status": "ok"}
```

### **Docker Health Checks**

```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# View container logs
docker logs text-to-image

# Check resource usage
docker stats text-to-image
```

### **PM2 Monitoring**

```bash
# Check PM2 status
pm2 status

# View logs
pm2 logs text-to-image

# Monitor resources
pm2 monit
```

### **Nginx Monitoring**

```bash
# Check Nginx status
sudo systemctl status nginx

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🔒 Security Considerations

### **Firewall Configuration**

```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### **SSL/TLS Configuration**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### **Environment Variable Security**

- Never commit `.env` files to version control
- Use secrets management in cloud platforms
- Rotate API tokens regularly
- Use least privilege principle

## 🚨 Troubleshooting

### **Common Issues**

**1. Port Already in Use**
```bash
# Find process using port
sudo lsof -i :3123

# Kill process
sudo kill -9 <PID>
```

**2. Docker Build Fails**
```bash
# Clear Docker cache
docker system prune -a

# Check disk space
df -h
```

**3. Memory Issues**
```bash
# Check memory usage
free -h

# Increase swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**4. Permission Issues**
```bash
# Fix file permissions
sudo chown -R $USER:$USER /path/to/project
chmod +x scripts/*.sh
```

### **Debug Commands**

```bash
# Check service status
systemctl status text-to-image

# View logs
journalctl -u text-to-image -f

# Test connectivity
curl -v http://localhost:3123/health

# Check environment variables
env | grep REPLICATE
```

## 📊 Performance Optimization

### **Docker Optimization**

```bash
# Use multi-stage builds
# Optimize layer caching
# Use .dockerignore effectively
```

### **Python Optimization**

```bash
# Use production WSGI server
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### **Nginx Optimization**

```nginx
# Enable gzip compression
gzip on;
gzip_types text/plain text/css application/json application/javascript;

# Enable caching
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 📈 Scaling

### **Horizontal Scaling**

```bash
# Run multiple instances
docker run -d -p 3123:3123 --env-file .env text-to-image
docker run -d -p 3124:3123 --env-file .env text-to-image
docker run -d -p 3125:3123 --env-file .env text-to-image
```

### **Load Balancing**

```nginx
upstream text_to_image {
    server localhost:3123;
    server localhost:3124;
    server localhost:3125;
}

server {
    listen 80;
    location / {
        proxy_pass http://text_to_image;
    }
}
```

### **Auto-scaling**

- Use cloud platform auto-scaling features
- Monitor CPU/memory usage
- Set appropriate scaling policies

---

**For more detailed information, refer to the [short-video-maker deployment patterns](https://github.com/gyoridavid/short-video-maker).** 