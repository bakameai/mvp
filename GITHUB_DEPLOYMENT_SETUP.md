# GitHub Actions Deployment Setup

This project is configured to automatically deploy the backend to Fly.io when you push to the `main` branch.

## Setup Steps

### 1. Get Your Fly.io API Token

```bash
flyctl auth token
```

Copy the token that's displayed.

### 2. Add Token to GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `FLY_API_TOKEN`
5. Value: Paste your Fly.io token
6. Click **Add secret**

### 3. Push Your Code

Once the secret is set up, any push to the `main` branch will automatically deploy:

```bash
git add .
git commit -m "Deploy OpenAI Realtime API integration"
git push origin main
```

### 4. Monitor Deployment

- Go to **Actions** tab in GitHub to see deployment progress
- Or check Fly.io logs: `flyctl logs -a app-pyzfduqr`

### 5. Update Telnyx Webhook

After successful deployment, update your Telnyx webhook to:
```
https://app-pyzfduqr.fly.dev/telnyx/incoming
```

## Manual Deployment Trigger

You can also trigger deployment manually:
1. Go to **Actions** tab in GitHub
2. Select **Deploy to Fly.io** workflow
3. Click **Run workflow**
4. Select branch and click **Run workflow**

## Troubleshooting

If deployment fails:
1. Check GitHub Actions logs for errors
2. Verify `FLY_API_TOKEN` secret is set correctly
3. Ensure Fly.io app exists: `flyctl apps list`
4. Check Fly.io secrets are set: `flyctl secrets list -a app-pyzfduqr`
