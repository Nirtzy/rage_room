# Setting Up PostgreSQL on Render

## Step 1: Create a PostgreSQL Database

1. Go to your Render dashboard: https://dashboard.render.com/
2. Click **"New +"** → **"PostgreSQL"**
3. Configure your database:
   - **Name**: `rage-room-db` (or any name you prefer)
   - **Database**: `rage_room`
   - **User**: (auto-generated)
   - **Region**: Same as your web service
   - **Plan**: **Free** (for testing)
4. Click **"Create Database"**

## Step 2: Connect Database to Your Web Service

1. Go to your **Web Service** (rage-room) on Render
2. Click **"Environment"** tab
3. Render should automatically add the `DATABASE_URL` environment variable
   - If not, add it manually by copying the **Internal Database URL** from your PostgreSQL database

## Step 3: Deploy

Your app will automatically:
- Detect the PostgreSQL database via `DATABASE_URL`
- Create the `messages` table on startup
- Store all messages in the database

## Step 4: Verify

1. After deployment, visit your app's `/health` endpoint:
   ```
   https://your-app.onrender.com/health
   ```

2. You should see:
   ```json
   {
     "status": "healthy",
     "message_count": 0,
     "connected_clients": 0,
     "date": "2026-01-12"
   }
   ```

## Testing Persistence

1. Send some messages in the chat
2. Wait a few seconds
3. Refresh your browser → **Messages should still be there!** ✅
4. Redeploy your app → **Messages should STILL be there!** ✅
5. At midnight → Messages will be cleared automatically 🌙

## Free Tier Limitations

Render's **free PostgreSQL** includes:
- ✅ 256 MB storage (enough for thousands of messages)
- ✅ Persistent data (survives restarts)
- ⚠️ Expires after 90 days (you'll need to migrate or upgrade)

For production use, upgrade to a paid plan ($7/month).

## Troubleshooting

### If you see "Package 'psycopg2-binary' is not satisfied"
This is just a warning in your local IDE. It will work fine on Render.

### If messages aren't persisting
1. Check Render logs for database connection errors
2. Verify `DATABASE_URL` environment variable is set
3. Look for "Database tables created successfully" in startup logs

### To view database contents
1. Go to your PostgreSQL database on Render
2. Click **"Shell"** tab
3. Run:
   ```sql
   SELECT * FROM messages;
   ```

## Local Development

For local development, the app uses **SQLite** automatically (no setup needed).

To use PostgreSQL locally:
1. Install PostgreSQL
2. Create a database
3. Set environment variable:
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/rage_room"
   ```

