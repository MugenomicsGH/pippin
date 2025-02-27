# Railway Deployment Guide

This guide explains how to deploy your Digital Being to Railway.

## Prerequisites

1. A Railway account (https://railway.app)
2. Node.js installed (for Railway CLI)
3. Your API keys ready:
   - Google API key
   - Midjourney API key
   - Twitter API credentials
   - Any other API keys your bot uses

## Deployment Steps

### 1. Install Railway CLI

```bash
npm i -g @railway/cli
```

### 2. Login to Railway

```bash
railway login
```

### 3. Initialize Railway Project

```bash
railway init
```

### 4. Set Environment Variables

Either through the Railway dashboard or CLI:

```bash
# Set required environment variables
railway vars set GOOGLE_API_KEY=your_google_api_key
railway vars set MJ_API_KEY=your_midjourney_api_key
railway vars set TWITTER_API_KEY=your_twitter_api_key
railway vars set TWITTER_API_SECRET=your_twitter_api_secret
railway vars set TWITTER_ACCESS_TOKEN=your_twitter_access_token
railway vars set TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
```

### 5. Deploy Your Application

```bash
railway up
```

### 6. Monitor Your Deployment

1. Visit the Railway dashboard
2. Click on your project
3. Check the "Deployments" tab for build and deployment status
4. View logs in the "Logs" tab

## Configuration Files

The deployment uses these configuration files:

1. `Dockerfile` - Defines how to build your application
2. `railway.toml` - Configures Railway-specific settings
3. `requirements.txt` - Lists Python dependencies

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check the build logs in Railway dashboard
   - Verify all dependencies are in requirements.txt
   - Ensure Dockerfile is correct

2. **Runtime Errors**
   - Check environment variables are set correctly
   - View logs in Railway dashboard
   - Verify config directory is properly created

3. **API Issues**
   - Confirm all API keys are set in Railway variables
   - Check API rate limits
   - Verify API endpoints are accessible

### Useful Commands

```bash
# View logs
railway logs

# SSH into the container
railway connect

# List environment variables
railway vars

# Restart the deployment
railway up
```

## Monitoring

Monitor your application through:

1. Railway Dashboard
2. Application logs
3. Your Twitter feed (for posted tweets)
4. Any monitoring endpoints you've set up

## Updates and Maintenance

To update your deployment:

1. Push changes to your repository
2. Railway will automatically detect changes and rebuild
3. Monitor the new deployment in the dashboard

Or manually trigger an update:
```bash
railway up
``` 