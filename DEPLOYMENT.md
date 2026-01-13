# Deployment Guide - Render with PostgreSQL

## Step-by-Step Deployment Instructions

### 1️⃣ Create PostgreSQL Database on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `rage-room-db`
   - **Database**: `rage_room` (or leave default)
   - **User**: (auto-generated)
   - **Region**: Choose closest to you (e.g., Oregon)
   - **PostgreSQL Version**: 16 (latest)
   - **Plan**: **Free** (for testing)
4. Click **"Create Database"**
5. **Wait 2-3 minutes** for database to be ready

### 2️⃣ Deploy Web Service

1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository:
   - Click **"Connect GitHub"** (if not already connected)
   - Search for: `Nirtzy/rage_room`
   - Click **"Connect"**

3. Configure the Web Service:

   **Basic Settings:**
   - **Name**: `rage-room` (or any name you like)
   - **Region**: Same as your database (e.g., Oregon)
   - **Branch**: `main`
   - **Root Directory**: (leave blank)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

   **Instance Type:**
   - **Plan**: **Free** (for testing)

4. Scroll down to **Environment Variables**:
   - Render should automatically detect your PostgreSQL database
   - If not, manually add:
     - **Key**: `DATABASE_URL`
     - **Value**: Copy the **Internal Database URL** from your PostgreSQL database page
     - Example: `postgresql://user:password@dpg-xxxxx/rage_room_xxxx`

5. Click **"Create Web Service"**

### 3️⃣ Monitor Deployment

1. You'll see the build logs in real-time
2. Look for these success messages:
   ```
   ==================================================
   SERVER STARTING UP
   Current date: 2026-01-13...
   Database tables created successfully
   Starting background tasks...
   Server startup complete!
   ==================================================
   INFO: Uvicorn running on http://0.0.0.0:10000
   ```

3. If successful, you'll see: **"Your service is live 🎉"**

### 4️⃣ Verify Deployment

1. Click on your service URL (e.g., `https://rage-room.onrender.com`)
2. You should see your chat application!
3. Test the health endpoint: `https://rage-room.onrender.com/health`
   - Should return: `{"status":"healthy","message_count":0,"connected_clients":0,"date":"2026-01-13"}`

### 5️⃣ Test Message Persistence

**Test that messages persist across deployments:**

1. Open your app: `https://rage-room.onrender.com`
2. Send a few test messages
3. Refresh the page → **Messages should still be there** ✅
4. Go to Render → **Manual Deploy** → **Clear build cache & deploy**
5. Wait for redeployment (~2-3 minutes)
6. Open app again → **Messages should STILL be there!** ✅
7. This proves PostgreSQL persistence is working!

## 🎯 What Happens Behind the Scenes

### On First Deployment:
1. Render builds your Python app
2. Installs dependencies (FastAPI, SQLAlchemy, psycopg2-binary, etc.)
3. Connects to PostgreSQL database using `DATABASE_URL`
4. Creates `messages` table automatically
5. Starts background tasks (midnight clearing, heartbeat)
6. Your app is live!

### Database Persistence:
- ✅ Messages saved to PostgreSQL (not in-memory)
- ✅ Survives server restarts
- ✅ Survives redeployments
- ✅ Messages cleared at midnight daily
- ✅ New users see message history

### Auto-Deployment:
- Every `git push` to `main` branch triggers automatic redeployment
- Zero downtime during updates (usually)

## ⚠️ Important Notes

### Free Tier Limitations:

**PostgreSQL (Free):**
- ✅ 256 MB storage (~thousands of messages)
- ✅ Persistent data
- ⚠️ **Expires after 90 days** - you'll need to migrate or upgrade
- ⚠️ Database will show expiry date in dashboard

**Web Service (Free):**
- ✅ 512 MB RAM
- ✅ Shared CPU
- ⚠️ **Spins down after 15 minutes of inactivity**
- ⚠️ First request after spin-down takes ~30 seconds (cold start)
- ⚠️ 750 hours/month (enough for testing)

### Upgrading (Optional):

**Option 1: Upgrade Web Service Only ($7/month)**
- ✅ **No spin-down** - App stays running 24/7
- ✅ **No cold starts** - Instant response times always
- ✅ **Better performance** - Dedicated resources
- ⚠️ Database still expires after 90 days (need to migrate)
- **Best for**: Apps with consistent traffic that need fast response

**Option 2: Upgrade PostgreSQL Only ($7/month)**
- ✅ **No expiration** - Database lasts forever
- ✅ **More storage** - Up to 1 GB (vs 256 MB free)
- ✅ **Better performance** - Faster queries
- ⚠️ Web service still spins down after 15 min inactivity
- **Best for**: Apps with important data but low/sporadic traffic

**Option 3: Upgrade Both ($14/month total)**
- ✅ **Production-ready** - 24/7 uptime, instant responses
- ✅ **Permanent database** - No data migration needed
- ✅ **Best performance** - Optimal for all use cases
- **Best for**: Serious projects, public-facing apps

**Recommendation for Rage Room:**
- **Testing/Demo**: Free tier is fine (just accept cold starts)
- **Active use**: Upgrade Web Service ($7/mo) for better UX
- **Long-term**: Upgrade both ($14/mo) to avoid 90-day migration

### 📊 Detailed Comparison:

| Feature | Free Tier | Web Service $7/mo | PostgreSQL $7/mo | Both $14/mo |
|---------|-----------|-------------------|------------------|-------------|
| **Uptime** | ⚠️ Spins down after 15 min | ✅ Always running | ⚠️ Spins down after 15 min | ✅ Always running |
| **Response Time** | ⚠️ 30s cold start | ✅ Instant | ⚠️ 30s cold start | ✅ Instant |
| **Database Expiry** | ⚠️ 90 days | ⚠️ 90 days | ✅ Never expires | ✅ Never expires |
| **Database Size** | 256 MB | 256 MB | 1 GB | 1 GB |
| **RAM** | 512 MB | 512 MB | 512 MB | 512 MB |
| **Storage** | Messages lost on expiry | Messages lost on expiry | ✅ Permanent | ✅ Permanent |
| **Best For** | Testing, demos | Active apps | Data archival | Production apps |
| **Monthly Cost** | **$0** | **$7** | **$7** | **$14** |

**What "spin down" means:**
- After 15 minutes with no visitors, the free web service turns off to save resources
- Next visitor waits ~30 seconds for server to "wake up" (cold start)
- Paid tier keeps server running 24/7 - no waiting, instant response

**What "cold start" means:**
- The delay when server needs to restart after spinning down
- Includes: loading Python, importing libraries, connecting to database
- Free tier: 20-40 seconds wait time
- Paid tier: Zero wait time (server never stops)

## 🔧 Troubleshooting

### Problem: "Address already in use" error
**Solution**: This is a local issue. On Render, it uses `$PORT` environment variable automatically.

### Problem: Database connection errors in logs
**Solution**: 
1. Check `DATABASE_URL` is set in Environment Variables
2. Verify it starts with `postgresql://` (not `postgres://`)
3. Our code auto-fixes this in `backend/config.py`

### Problem: Messages not persisting
**Solution**:
1. Check Render logs for database errors
2. Verify `DATABASE_URL` is correct
3. Look for "Database tables created successfully" in logs

### Problem: App shows "Service Unavailable"
**Solution**:
1. Check Render logs for errors
2. Verify build completed successfully
3. Check if web service is running (not suspended)

### Problem: Cold starts are slow (free tier)
**Solution**: 
- This is normal for free tier
- Upgrade to paid plan for instant responses
- Or accept 15-30 second first load after inactivity

## 📊 Monitoring Your App

### View Logs:
1. Go to your Web Service in Render
2. Click **"Logs"** tab
3. See real-time logs:
   - `[HEARTBEAT]` - Every 5 minutes
   - Message sending/receiving
   - Database operations
   - Midnight message clearing

### Check Database:
1. Go to your PostgreSQL database in Render
2. Click **"Shell"** tab
3. Run SQL commands:
   ```sql
   -- See all messages
   SELECT * FROM messages;
   
   -- Count today's messages
   SELECT COUNT(*) FROM messages WHERE date_created = '2026-01-13';
   
   -- Delete all messages (manual clear)
   DELETE FROM messages;
   ```

## 🚀 Your App URLs

After deployment, you'll have:
- **Main App**: `https://rage-room.onrender.com`
- **Health Check**: `https://rage-room.onrender.com/health`
- **API Docs**: `https://rage-room.onrender.com/docs` (auto-generated by FastAPI!)

## ✅ Deployment Checklist

- [ ] PostgreSQL database created on Render
- [ ] Web Service created and connected to GitHub
- [ ] `DATABASE_URL` environment variable set
- [ ] Build successful (check logs)
- [ ] App accessible via URL
- [ ] Health check returns `{"status": "healthy"}`
- [ ] Can send and receive messages
- [ ] Messages persist after page refresh
- [ ] Messages persist after redeployment
- [ ] Nickname timer works (10 minutes)
- [ ] Rate limiting works (25 messages/minute)

## ❓ Frequently Asked Questions

### What happens when the 10-minute timer runs out?

**Behavior:**
1. Timer counts down from 10:00 to 0:00
2. When **30 seconds remain** (0:30), timer turns **red** as a warning
3. When timer hits **0:00**:
   - Page automatically reloads
   - New nickname is generated
   - User can continue chatting with new identity
   - Chat history remains visible (from database)

**User Experience:**
- ⚠️ Users lose any message they're currently typing
- ✅ They can immediately start chatting again with new nickname
- ✅ All previous messages stay visible
- ✅ Clear visual warning (red timer) before reload

**Why 10 minutes?**
- Prevents spam by limiting rapid nickname changes
- Provides temporary accountability
- Maintains anonymity (no permanent identity)
- Rate limiting tracks by nickname (25 msg/min per user)

### Can users extend their timer?

**No** - this is intentional to maintain fairness:
- Prevents users from "camping" on a nickname forever
- Ensures everyone gets fresh identities periodically
- Maintains the "rage room" concept of temporary venting

### What if someone refreshes the page before 10 minutes?

**Timer persists!** 
- Nickname and timer stored in browser's `localStorage`
- Refreshing the page keeps the same nickname
- Timer continues counting down from where it was
- Only resets after 10 full minutes expire

### How do I change the daily topic without redeploying?

**Use Environment Variables on Render:**

1. Go to your Web Service on Render Dashboard
2. Click **"Environment"** tab
3. Add these environment variables:
   - **Key**: `DAILY_TOPIC`
   - **Value**: `why is coffee so expensive?` (or any topic you want)
   
   - **Key**: `DAILY_RULES` (optional)
   - **Value**: `keep it civil!` (or any rules)

4. Click **"Save Changes"**
5. Render automatically restarts your service (takes ~30 seconds)
6. Your new topic appears immediately!

**No code changes or redeployment needed!**

**Examples:**
- `DAILY_TOPIC=why is traffic so bad?`
- `DAILY_TOPIC=what's wrong with customer service?`
- `DAILY_TOPIC=Monday mornings, am I right?`

**Default topic** (if not set): `"what you think about ICE?"`

---

**You're all set!** 🎉 Your Rage Room is now live with PostgreSQL persistence!

