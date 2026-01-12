# Rage Room - Daily Chat Application

A real-time chat application where messages are cleared daily at midnight. Users can discuss daily topics anonymously.

## Features

- 🔒 **Secure**: Rate limiting, input sanitization, connection limits
- 💾 **Persistent**: Messages stored in PostgreSQL database
- 🌙 **Daily Reset**: Messages automatically cleared at midnight
- ⚡ **Real-time**: WebSocket-based live chat
- 🎭 **Anonymous**: Random nicknames for each user

## Project Structure

```
backend/
├── main.py          # FastAPI app initialization
├── config.py        # Configuration and environment variables
├── database.py      # Database connection and session management
├── models.py        # SQLAlchemy database models
├── routes.py        # API endpoints
├── websocket.py     # WebSocket handling and background tasks
└── utils.py         # Helper functions (rate limiting, sanitization)

static/
├── index.html       # Frontend HTML
├── script.js        # Frontend JavaScript
└── styles.css       # Frontend CSS
```

## Setup

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   uvicorn backend.main:app --reload
   ```

3. **Access the app:**
   Open http://localhost:8000

### Deployment on Render

1. **Create a PostgreSQL database** on Render
2. **Add environment variable** `DATABASE_URL` (automatically set by Render)
3. **Deploy** from GitHub repository

The app will automatically:
- Create database tables on startup
- Use PostgreSQL for message persistence
- Clear old messages at midnight

## Configuration

Edit `backend/config.py` to customize:

- `MAX_MESSAGES_PER_MINUTE`: Rate limit per user (default: 25)
- `MAX_MESSAGE_LENGTH`: Maximum message length (default: 500)
- `MAX_CONNECTIONS`: Maximum concurrent connections (default: 100)
- `ALLOWED_ORIGINS`: CORS allowed origins

## API Endpoints

- `GET /` - Main chat interface
- `GET /health` - Health check (shows message count, connected clients)
- `GET /api/today` - Get today's topic information
- `GET /api/messages` - Get message history for today
- `WebSocket /ws` - Real-time chat connection

## Security Features

- ✅ Rate limiting (prevents spam)
- ✅ Input sanitization (prevents XSS)
- ✅ Message length limits
- ✅ Connection limits
- ✅ CORS protection
- ✅ Automatic daily message clearing

## License

MIT

