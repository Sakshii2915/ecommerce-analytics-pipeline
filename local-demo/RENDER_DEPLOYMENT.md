# Deploy E-Commerce Analytics Dashboard on Render

This guide will help you deploy the analytics dashboard to Render.com.

## Prerequisites

1. GitHub account (your code is already on GitHub)
2. Render account (sign up at https://render.com - free tier available)

## Step 1: Prepare Your Repository

Make sure all files are committed and pushed to GitHub:

```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

## Step 2: Deploy on Render

### Option A: Deploy via Render Dashboard (Recommended)

1. **Sign in to Render**
   - Go to https://render.com
   - Sign in with your GitHub account

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select: `Sakshii2915/ecommerce-analytics-pipeline`

3. **Configure Service**
   - **Name**: `ecommerce-analytics-dashboard`
   - **Root Directory**: `local-demo`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python setup_render.py`
   - **Start Command**: `python dashboard.py`
   - **Plan**: Free (or choose paid for better performance)

4. **Environment Variables** (Optional)
   - `PORT`: `8050` (Render will set this automatically)
   - `DEBUG`: `False` (for production)

5. **Click "Create Web Service"**
   - Render will start building and deploying your app
   - This takes 5-10 minutes the first time

6. **Wait for Deployment**
   - Watch the build logs
   - Once deployed, you'll get a URL like: `https://ecommerce-analytics-dashboard.onrender.com`

### Option B: Deploy via Render Blueprint (render.yaml)

1. **Go to Render Dashboard**
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Select: `Sakshii2915/ecommerce-analytics-pipeline`

2. **Render will automatically detect `render.yaml`**
   - It will create the service with the configuration
   - Click "Apply"

## Step 3: Verify Deployment

1. **Check Build Logs**
   - Go to your service dashboard
   - Check "Logs" tab for any errors

2. **Test the Dashboard**
   - Open the provided URL
   - You should see the analytics dashboard with:
     - KPI cards
     - Revenue charts
     - Transaction analytics

## Step 4: Custom Domain (Optional)

1. **Add Custom Domain**
   - Go to your service settings
   - Click "Custom Domains"
   - Add your domain name
   - Follow DNS configuration instructions

## Troubleshooting

### Build Fails

**Issue**: Build command fails
- **Solution**: Check that all dependencies are in `requirements.txt`
- Verify Python version matches `runtime.txt`

**Issue**: Data generation takes too long
- **Solution**: Reduce `NUM_TRANSACTIONS` in `generate_data.py` (default: 100,000)
- Or pre-generate data and commit it to the repo

### Dashboard Not Loading

**Issue**: "Application Error"
- **Solution**: Check logs in Render dashboard
- Verify `setup_render.py` completed successfully
- Ensure database file was created

**Issue**: Port binding error
- **Solution**: Dashboard should use `PORT` environment variable (already configured)

### Performance Issues

**Issue**: Slow loading
- **Solution**: 
  - Upgrade to paid plan for better resources
  - Reduce data size
  - Use pre-generated data instead of generating on deploy

## Render Free Tier Limits

- **512 MB RAM**
- **0.1 CPU**
- **Spins down after 15 minutes of inactivity**
- **Takes ~30 seconds to wake up**

## Updating Your Deployment

1. **Push changes to GitHub**
   ```bash
   git add .
   git commit -m "Update dashboard"
   git push origin main
   ```

2. **Render will automatically redeploy**
   - Go to Render dashboard
   - Click "Manual Deploy" → "Deploy latest commit"

## Cost

- **Free Tier**: $0/month (with limitations)
- **Starter Plan**: $7/month (always-on, better performance)
- **Standard Plan**: $25/month (production-ready)

## Next Steps

1. ✅ Dashboard deployed on Render
2. 🔄 Set up auto-deploy from GitHub
3. 📊 Share your dashboard URL
4. 🚀 Consider upgrading for production use

## Support

- Render Documentation: https://render.com/docs
- Render Community: https://community.render.com
- GitHub Issues: Create an issue in your repository

---

**Your dashboard will be live at**: `https://[your-service-name].onrender.com`


