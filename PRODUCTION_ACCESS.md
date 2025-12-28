# Admin Access for Production

This guide explains how to create a Super Admin user for your **live production site** (calleem.tech).

## Prerequisites

1.  **Railway Account Access:** You need to get your production connection string.
2.  **Terminal Access:** You must run the script from your local machine.

## Step 1: Get Production MongoDB URI

1.  Log in to your [Railway Dashboard](https://railway.app).
2.  Click on your **Proejct**.
3.  Select your **MongoDB** service.
4.  Go to the **Variables** tab.
5.  Copy the value of `MONGO_URL` (it looks like `mongodb://mongo:kxji...`).
    *   *Note: If the `MONGO_URL` is internal (starts with `mongodb://mongo:`), you might need the **Public Public Networking** URL if you are running this from your laptop. Go to "Settings" > "Networking" and copy the "Public TCP Proxy" URL (e.g., `mongodb://roundhouse.proxy.rlwy.net:12345`).*

## Step 2: Run the Creation Script

In your local terminal (inside the project folder), run:

```bash
python3 scripts/create_super_admin.py
```

## Step 3: Follow the Prompts

1.  **MongoDB URI:** Paste the connection string you copied in Step 1.
    *   *Warning:* If it asks for confirmation to connect to a remote DB, type `yes`.
2.  **Email:** Enter `admin@calleem.com` (or your preferred email).
3.  **Username:** Enter `superadmin`.
4.  **Password:** Create a STRONG password (e.g., `CalleemMaster2025!`).

## Step 4: Verify Access

1.  Go to [https://calleem.tech/admin/login](https://calleem.tech/admin/login).
2.  Log in with the credentials you just created.
3.  You should be redirected to the secure admin dashboard.
