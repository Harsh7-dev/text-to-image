# Deployment Guide - Railway

This guide will help you deploy your Text-to-Image API to Railway.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Account**: Your code should be in a GitHub repository
3. **Replicate API Token**: Get your token from [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens)

## Deployment Steps

### 1. Prepare Your Repository

Make sure your repository has these files:
- `Dockerfile`
- `railway.json`
- `requirements.txt`
- `app/main.py`
- `app/static/index.html`
- `.env` (with your Replicate token)

### 2. Deploy to Railway

1. **Connect Repository**:
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

2. **Configure Environment Variables**:
   - In your Railway project dashboard
   - Go to "Variables" tab
   - Add the following variable:
     - `REPLICATE_API_TOKEN`: Your Replicate API token (starts with `r8_`)

3. **Deploy**:
   - Railway will automatically detect the Dockerfile and deploy
   - The build process will take a few minutes
   - You'll get a URL like `https://your-app-name.railway.app`

### 3. Verify Deployment

1. **Check Health**: Visit `https://your-app-name.railway.app/health`
2. **Test Frontend**: Visit `https://your-app-name.railway.app/`
3. **Test API**: Use the web interface to generate an image

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `REPLICATE_API_TOKEN` | Your Replicate API token | Yes |
| `PORT` | Port for the application (set by Railway) | No |

## Custom Domain (Optional)

1. In Railway dashboard, go to "Settings"
2. Click "Custom Domains"
3. Add your domain and configure DNS

## Monitoring

- **Logs**: View real-time logs in Railway dashboard
- **Metrics**: Monitor CPU, memory, and network usage
- **Health Checks**: Automatic health checks every 30 seconds

## Troubleshooting

### Common Issues

1. **Build Fails**:
   - Check that all required files are in the repository
   - Verify the Dockerfile syntax
   - Check Railway logs for specific errors

2. **Environment Variables**:
   - Ensure `REPLICATE_API_TOKEN` is set in Railway variables
   - Token should start with `r8_`

3. **App Not Starting**:
   - Check the logs in Railway dashboard
   - Verify the health check endpoint works
   - Ensure the port configuration is correct

4. **API Errors**:
   - Verify your Replicate token is valid
   - Check that you have sufficient credits on Replicate
   - Ensure the model is accessible

### Getting Help

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- **Replicate Docs**: [replicate.com/docs](https://replicate.com/docs)

## Cost Optimization

- Railway offers a free tier with usage limits
- Monitor your usage in the Railway dashboard
- Consider upgrading if you exceed free tier limits
- Replicate charges per API call - monitor usage there too

## Security Notes

- Never commit your `.env` file to Git
- Use Railway's environment variables for secrets
- The app runs as a non-root user in the container
- Health checks help ensure the app is running properly 