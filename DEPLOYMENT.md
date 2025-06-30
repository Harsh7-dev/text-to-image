# Railway Deployment Guide

This guide will help you deploy your Text-to-Image API on Railway.

## Prerequisites

1. A GitHub account with your repository pushed
2. A Railway account (free tier available)
3. A Replicate account with API token

## Step 1: Create Railway Account

1. Go to [Railway.app](https://railway.app)
2. Sign up with your GitHub account
3. Complete the verification process

## Step 2: Deploy from GitHub

1. **Connect GitHub Repository:**
   - In Railway dashboard, click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository from the list
   - Click "Deploy Now"

2. **Configure Environment Variables:**
   - Go to your project's "Variables" tab
   - Add the following environment variables:
   
   ```
   REPLICATE_API_TOKEN=your_replicate_token_here
   ```
   
   - Get your Replicate token from: https://replicate.com/account/api-tokens
   - Click "Add" to save each variable

3. **Deploy:**
   - Railway will automatically build and deploy your application
   - The build process uses the Dockerfile in your repository
   - You can monitor the build logs in real-time

## Step 3: Access Your Application

1. **Get Your Domain:**
   - Once deployed, go to the "Settings" tab
   - Copy your custom domain (e.g., `your-app-name.railway.app`)
   - Or use the generated Railway domain

2. **Test Your API:**
   - Health check: `https://your-domain.railway.app/health`
   - Generate endpoint: `https://your-domain.railway.app/generate`

## Step 4: Custom Domain (Optional)

1. In Railway dashboard, go to "Settings"
2. Click "Custom Domains"
3. Add your domain and configure DNS records
4. Railway will provide the necessary DNS configuration

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `REPLICATE_API_TOKEN` | Your Replicate API token for image generation | Yes | None |
| `PORT` | Port for the application | No | 8000 |

## Troubleshooting

### Build Failures
- Check the build logs in Railway dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify Dockerfile syntax

### Runtime Errors
- Check application logs in Railway dashboard
- Verify environment variables are set correctly
- Ensure your Replicate token is valid and has sufficient credits

### Health Check Failures
- The `/health` endpoint should return 200 OK
- Check if the application is starting correctly
- Verify port configuration

## Monitoring

- **Logs:** View real-time logs in Railway dashboard
- **Metrics:** Monitor CPU, memory, and network usage
- **Deployments:** Track deployment history and rollback if needed

## Cost Optimization

- Railway offers a free tier with usage limits
- Monitor your usage in the dashboard
- Consider upgrading for production workloads
- Replicate charges per API call - monitor usage there too

## Security

- Never commit API tokens to your repository
- Use Railway's environment variables for sensitive data
- Enable automatic deployments only for trusted branches 