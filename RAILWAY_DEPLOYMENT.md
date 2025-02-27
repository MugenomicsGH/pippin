# Railway Deployment Guide

This guide explains how to deploy your Digital Being to Railway using Nixpacks.

## Prerequisites

1. A Railway account (https://railway.app)
2. Your API keys ready:
   - Google API key
   - Midjourney API key
   - Twitter API credentials
   - Any other API keys your bot uses

## Deployment Steps

### 1. Initial Setup

1. Go to Railway.app
2. Create a new project
3. Click "Add Service"
4. Select "GitHub Repo"
5. Choose your repository

### 2. Configure Build Settings

In your service settings:

1. Builder: Nixpacks (default)
2. Start Command: `python -m framework.main`
3. Watch Path: `/` (or your project subdirectory if not in root)

### 3. Set Environment Variables

In the Variables tab, add:

```bash
GOOGLE_API_KEY=your_google_api_key
MJ_API_KEY=your_midjourney_api_key
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
PYTHON_ENV=production
PORT=8000
PYTHONUNBUFFERED=1
```

### 4. Deploy

1. Railway will automatically detect your Python project
2. It will install dependencies from requirements.txt
3. The service will start using the specified start command

## Project Structure Requirements

Ensure your repository has:

1. `requirements.txt` in the root directory
2. Python version specified (Nixpacks will detect this automatically)
3. Your main application code
4. Config directory setup (copied from config_sample)

## Monitoring

Monitor your application through:

1. Railway Dashboard
2. Application logs
3. Your Twitter feed (for posted tweets)
4. Any monitoring endpoints you've set up

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check requirements.txt is in the correct location
   - Verify all dependencies are listed correctly
   - Check Python version compatibility

2. **Runtime Errors**
   - Check environment variables are set correctly
   - View logs in Railway dashboard
   - Verify config directory is properly created

3. **API Issues**
   - Confirm all API keys are set in Railway variables
   - Check API rate limits
   - Verify API endpoints are accessible

### Useful Commands

If you choose to use the Railway CLI (optional):

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# View logs
railway logs

# List environment variables
railway vars

# Deploy latest changes
railway up
```

## Updates and Maintenance

To update your deployment:

1. Push changes to your GitHub repository
2. Railway will automatically detect changes and rebuild
3. Monitor the new deployment in the dashboard

## Best Practices

1. Keep requirements.txt up to date
2. Use specific version numbers in requirements.txt
3. Test locally before pushing changes
4. Monitor logs after deployments
5. Set up automated health checks 