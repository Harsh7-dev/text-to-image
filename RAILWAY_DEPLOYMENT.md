# Railway Deployment Guide

This guide will help you deploy your text-to-image application to Railway.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Environment Variables**: You'll need to set up your API keys

## Deployment Steps

### 1. Connect to Railway

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your text-to-image repository

### 2. Configure Environment Variables

In your Railway project dashboard, go to the "Variables" tab and add these environment variables:

```
LANGTRACE_API_KEY=f757aeaa9dcb99f3419da8233c4485f9a5140841b23f22fa04bf2b683e3a827f
REPLICATE_API_TOKEN=your_replicate_api_token_here
```

**Important**: Replace `your_replicate_api_token_here` with your actual Replicate API token.

### 3. Deploy

1. Railway will automatically detect the Dockerfile and start building
2. The build process will install dependencies and create the container
3. Once built, Railway will deploy your application
4. You'll get a public URL for your application

### 4. Verify Deployment

1. Check the deployment logs in Railway dashboard
2. Visit your application URL and test the endpoints:
   - Health check: `https://your-app.railway.app/health`
   - Test trace: `https://your-app.railway.app/test-trace`
   - Generate image: `https://your-app.railway.app/api/generate-image`

### 5. Monitor and Debug

- **Logs**: Check the "Deployments" tab for logs
- **Health Checks**: Railway will automatically monitor your `/health` endpoint
- **Tracing**: Check your Langtrace dashboard for traces from the deployed app

## Configuration Files

### railway.json
- Specifies Dockerfile as the build method
- Sets health check endpoint to `/health`
- Configures restart policy

### Dockerfile
- Uses Python 3.12 slim image
- Installs dependencies from requirements.txt
- Runs as non-root user for security
- Exposes port via Railway's PORT environment variable

### .dockerignore
- Excludes unnecessary files from build context
- Reduces build time and image size

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `LANGTRACE_API_KEY` | Your Langtrace API key for tracing | Yes |
| `REPLICATE_API_TOKEN` | Your Replicate API token for image generation | Yes |
| `PORT` | Port number (set automatically by Railway) | No |

## Troubleshooting

### Build Failures
- Check that all dependencies are in `requirements.txt`
- Verify the Dockerfile syntax
- Check Railway build logs for specific errors

### Runtime Errors
- Check application logs in Railway dashboard
- Verify environment variables are set correctly
- Test endpoints manually

### Health Check Failures
- Ensure `/health` endpoint returns 200 OK
- Check if the application is starting correctly
- Verify port configuration

## Scaling

Railway automatically scales your application based on traffic. You can also:
- Set custom scaling rules in the Railway dashboard
- Configure resource limits
- Set up custom domains

## Cost Optimization

- Railway charges based on usage
- Consider setting up auto-sleep for development environments
- Monitor usage in the Railway dashboard

## Security

- Environment variables are encrypted
- Application runs as non-root user
- Health checks ensure application availability
- Automatic restarts on failures 