# Deployment Guide

## Production URLs

- **Railway Backend**: https://ai-receptionist-production-299a.up.railway.app
- **Vercel Frontend**: https://aireceptionist-lake.vercel.app

## Vercel Configuration

### Environment Variables

Set the following environment variable in Vercel Dashboard:

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add the following:

```
NEXT_PUBLIC_API_URL=https://ai-receptionist-production-299a.up.railway.app
```

### Automatic Deployment

Vercel automatically deploys when you push to the main/master branch on GitHub.

To trigger a deployment:
```bash
git push origin master
```

## Railway Configuration

### Environment Variables

Set the following environment variables in Railway Dashboard:

1. Go to your Railway project dashboard
2. Navigate to **Variables** tab
3. Add the following:

```
CORS_ORIGINS=https://aireceptionist-lake.vercel.app
FRONTEND_URL=https://aireceptionist-lake.vercel.app
ENVIRONMENT=production
```

### Required Variables

- `MONGO_URI` - MongoDB connection string
- `SECRET_KEY` - Strong secret key for JWT (generate with: `python -c 'import secrets; print(secrets.token_urlsafe(32))'`)
- `CORS_ORIGINS` - Comma-separated list of allowed origins
- `FRONTEND_URL` - Your Vercel frontend URL
- `ENVIRONMENT=production`

## Testing Production

After deployment, test the production endpoints:

```bash
./scripts/test_production.sh
```

This will test:
- Railway backend health endpoints
- API endpoints
- Vercel frontend pages
- CORS configuration

## Manual Testing

### Test Backend
```bash
curl https://ai-receptionist-production-299a.up.railway.app/health
curl https://ai-receptionist-production-299a.up.railway.app/
```

### Test Frontend
```bash
curl https://aireceptionist-lake.vercel.app
```

### Test CORS
```bash
curl -X OPTIONS \
  -H "Origin: https://aireceptionist-lake.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  https://ai-receptionist-production-299a.up.railway.app/api/v1/users/register
```

## Troubleshooting

### CORS Errors

If you see CORS errors:
1. Verify `CORS_ORIGINS` and `FRONTEND_URL` are set in Railway
2. Check that the Vercel URL matches exactly (including https://)
3. Restart the Railway service after updating environment variables

### Frontend Can't Connect to Backend

1. Verify `NEXT_PUBLIC_API_URL` is set in Vercel
2. Check that the Railway URL is correct and accessible
3. Rebuild the Vercel deployment after setting environment variables

### Backend Not Responding

1. Check Railway logs: Railway Dashboard → Deployments → View Logs
2. Verify MongoDB connection string is correct
3. Check that all required environment variables are set

