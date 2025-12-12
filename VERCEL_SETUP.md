# Vercel Setup Instructions

## ✅ Production URLs

- **Railway Backend**: https://ai-receptionist-production-299a.up.railway.app
- **Vercel Frontend**: https://aireceptionist-lake.vercel.app

## 🔧 Required Vercel Configuration

### Step 1: Set Environment Variable

1. Go to your Vercel Dashboard: https://vercel.com/dashboard
2. Select your project: `aireceptionist-lake` (or your project name)
3. Navigate to **Settings** → **Environment Variables**
4. Click **Add New**
5. Add the following:

   **Variable Name**: `NEXT_PUBLIC_API_URL`
   
   **Value**: `https://ai-receptionist-production-299a.up.railway.app`
   
   **Environment**: Select all (Production, Preview, Development)

6. Click **Save**

### Step 2: Redeploy

After adding the environment variable:

1. Go to **Deployments** tab
2. Click the **⋯** (three dots) on the latest deployment
3. Select **Redeploy**
4. Or simply push a new commit to trigger automatic deployment

## ✅ Test Results

All production endpoints are working:

- ✅ Railway Backend Health: `200 OK`
- ✅ Railway API Docs: `200 OK`
- ✅ Vercel Frontend: `200 OK`
- ✅ CORS Preflight: `200 OK`

## 🧪 Test Production

After setting the environment variable and redeploying, test with:

```bash
./scripts/test_production.sh
```

Or manually test:

```bash
# Test backend
curl https://ai-receptionist-production-299a.up.railway.app/health

# Test frontend
curl https://aireceptionist-lake.vercel.app

# Test CORS
curl -X OPTIONS \
  -H "Origin: https://aireceptionist-lake.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  https://ai-receptionist-production-299a.up.railway.app/api/v1/users/register
```

## 📝 Notes

- The environment variable `NEXT_PUBLIC_API_URL` must be set in Vercel for the frontend to connect to the backend
- After setting the variable, you must redeploy for changes to take effect
- The Railway backend is already configured with CORS to allow requests from the Vercel frontend

