# 🏗️ Rage Room - Architecture & System Design

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ index.html   │  │ login.html   │  │ admin.html   │         │
│  │ (Main Chat)  │  │ (Auth Page)  │  │ (Admin UI)   │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                 │                  │                  │
│         └─────────────────┼──────────────────┘                  │
│                           │                                     │
│                    ┌──────▼──────┐                             │
│                    │  script.js  │                             │
│                    │  (Frontend) │                             │
│                    └──────┬──────┘                             │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                            │ HTTP/WebSocket
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    FASTAPI SERVER (Backend)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    main.py                               │   │
│  │  • App Initialization                                    │   │
│  │  • CORS Middleware                                       │   │
│  │  • Static File Serving                                  │   │
│  │  • Route Registration                                    │   │
│  │  • Lifespan Management (Startup/Shutdown)                │   │
│  └───────┬──────────────────────────────────────────────────┘   │
│          │                                                       │
│          ├──────────────────────────────────────┐              │
│          │                                      │              │
│  ┌───────▼────────┐  ┌──────────────┐  ┌──────▼────────┐     │
│  │  routes.py     │  │ auth_routes  │  │ admin_routes  │     │
│  │  • GET /       │  │ • POST /login│  │ • GET /stats  │     │
│  │  • GET /health │  │ • POST /reg  │  │ • POST /topic │     │
│  │  • GET /api/*  │  │ • GET /me    │  │ • DELETE /msg │     │
│  └───────┬────────┘  └──────┬───────┘  └──────┬────────┘     │
│          │                  │                  │               │
│          │                  │                  │               │
│  ┌───────▼──────────────────▼──────────────────▼────────┐     │
│  │              auth.py (Authentication)                 │     │
│  │  • JWT Token Creation/Validation                      │     │
│  │  • Password Hashing (bcrypt)                        │     │
│  │  • User Authentication                               │     │
│  │  • Admin Authorization                                │     │
│  └───────────────────────┬──────────────────────────────┘     │
│                          │                                      │
│  ┌───────────────────────▼──────────────────────────────┐      │
│  │              websocket.py                            │      │
│  │  • WebSocket Connection Handling                     │      │
│  │  • Message Broadcasting                              │      │
│  │  • Rate Limiting (utils.py)                         │      │
│  │  • Background Tasks:                                │      │
│  │    - midnight_clear_task()                          │      │
│  │    - keep_alive_task()                              │      │
│  └───────────────────────┬──────────────────────────────┘      │
│                          │                                      │
│  ┌───────────────────────▼──────────────────────────────┐     │
│  │              database.py                              │     │
│  │  • SQLAlchemy Engine                                  │     │
│  │  • Session Management                                 │     │
│  │  • Connection Pooling                                 │     │
│  └───────────────────────┬──────────────────────────────┘     │
│                          │                                      │
│  ┌───────────────────────▼──────────────────────────────┐     │
│  │              models.py                                │     │
│  │  • User Model (SQLAlchemy)                            │     │
│  │  • Message Model (SQLAlchemy)                         │     │
│  └───────────────────────┬──────────────────────────────┘     │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                           │ SQL Queries
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    DATABASE (PostgreSQL)                         │
│  ┌──────────────────┐        ┌──────────────────┐             │
│  │   users table    │        │  messages table  │             │
│  │  • id            │        │  • id            │             │
│  │  • email         │        │  • user          │             │
│  │  • username      │        │  • text          │             │
│  │  • password_hash │        │  • timestamp     │             │
│  │  • is_admin      │        │  • date_created │             │
│  │  • is_active     │        │  • user_id (FK)  │             │
│  └──────────────────┘        └──────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### 1. User Registration Flow

```
User → login.html
  │
  ├─> Fills registration form
  │
  ├─> POST /api/auth/register
  │     │
  │     ├─> auth_routes.py::register()
  │     │     │
  │     │     ├─> Check email exists? → Error
  │     │     ├─> Check username exists? → Error
  │     │     │
  │     │     ├─> auth.py::get_password_hash()
  │     │     │     │
  │     │     │     └─> bcrypt.hash() → hashed_password
  │     │     │
  │     │     ├─> models.py::User()
  │     │     │     │
  │     │     │     └─> Create User instance
  │     │     │
  │     │     └─> database.py::db.commit()
  │     │           │
  │     │           └─> Save to PostgreSQL
  │     │
  │     └─> Return UserResponse (201 Created)
  │
  └─> Show success message → Switch to login tab
```

### 2. User Login Flow

```
User → login.html
  │
  ├─> Fills login form
  │
  ├─> POST /api/auth/login
  │     │
  │     ├─> auth_routes.py::login()
  │     │     │
  │     │     ├─> auth.py::authenticate_user()
  │     │     │     │
  │     │     │     ├─> Query User by email
  │     │     │     │
  │     │     │     ├─> auth.py::verify_password()
  │     │     │     │     │
  │     │     │     │     └─> bcrypt.verify() → True/False
  │     │     │     │
  │     │     │     └─> Return User or None
  │     │     │
  │     │     ├─> auth.py::create_access_token()
  │     │     │     │
  │     │     │     └─> jwt.encode() → JWT Token
  │     │     │
  │     │     └─> Return Token (200 OK)
  │     │
  │     ├─> GET /api/auth/me (with Bearer token)
  │     │     │
  │     │     ├─> auth.py::get_current_user()
  │     │     │     │
  │     │     │     ├─> jwt.decode() → user_id
  │     │     │     │
  │     │     │     └─> Query User by id
  │     │     │
  │     │     └─> Return UserResponse
  │     │
  │     └─> Save token to localStorage
  │
  └─> Redirect to / or /static/admin.html
```

### 3. Chat Message Flow (WebSocket)

```
User → index.html
  │
  ├─> Types message
  │
  ├─> WebSocket.send() → /ws
  │     │
  │     ├─> websocket.py::websocket_endpoint()
  │     │     │
  │     │     ├─> Accept connection
  │     │     │     │
  │     │     │     └─> Add to connected_clients set
  │     │     │
  │     │     ├─> Send message history (today's messages)
  │     │     │
  │     │     ├─> Receive new message
  │     │     │     │
  │     │     │     ├─> schemas.py::MessageCreate (validation)
  │     │     │     │
  │     │     │     ├─> utils.py::is_rate_limited()
  │     │     │     │     │
  │     │     │     │     └─> Check if user sent >25 msgs/min
  │     │     │     │
  │     │     │     ├─> models.py::Message()
  │     │     │     │     │
  │     │     │     │     └─> Create Message instance
  │     │     │     │
  │     │     │     ├─> database.py::db.commit()
  │     │     │     │     │
  │     │     │     │     └─> Save to PostgreSQL
  │     │     │     │
  │     │     │     └─> websocket.py::broadcast()
  │     │     │           │
  │     │     │           └─> Send to all connected_clients
  │     │     │
  │     │     └─> Loop continues...
  │     │
  │     └─> Client receives message → Update UI
  │
  └─> Message appears in chat
```

### 4. Admin Dashboard Flow

```
Admin → admin.html
  │
  ├─> Check localStorage for token
  │
  ├─> GET /api/auth/me (with Bearer token)
  │     │
  │     ├─> auth.py::get_current_admin_user()
  │     │     │
  │     │     ├─> Verify token
  │     │     │
  │     │     └─> Check is_admin == True
  │     │
  │     └─> Return User
  │
  ├─> GET /api/admin/stats
  │     │
  │     ├─> admin_routes.py::get_statistics()
  │     │     │
  │     │     ├─> Query count(User)
  │     │     ├─> Query count(Message)
  │     │     └─> Query count(Message WHERE date_created = today)
  │     │
  │     └─> Return statistics
  │
  ├─> GET /api/admin/messages
  │     │
  │     └─> Return all messages (paginated)
  │
  └─> Display in admin UI
```

## Component Responsibilities

### Backend Components

| Component | Responsibility | Key Functions |
|-----------|---------------|---------------|
| **main.py** | Application entry point | • Initialize FastAPI app<br>• Configure CORS<br>• Register routes<br>• Startup/shutdown logic |
| **config.py** | Configuration management | • Environment variables<br>• Database URL<br>• JWT settings<br>• Security settings |
| **database.py** | Database connection | • SQLAlchemy engine<br>• Session factory<br>• Connection pooling |
| **models.py** | Data models | • User model<br>• Message model<br>• Database schema |
| **schemas.py** | Request/response validation | • Pydantic models<br>• Input validation<br>• Data sanitization |
| **auth.py** | Authentication logic | • JWT token creation/validation<br>• Password hashing<br>• User authentication |
| **auth_routes.py** | Auth API endpoints | • POST /api/auth/register<br>• POST /api/auth/login<br>• GET /api/auth/me |
| **admin_routes.py** | Admin API endpoints | • GET /api/admin/stats<br>• POST /api/admin/topic<br>• DELETE /api/admin/message |
| **routes.py** | General API endpoints | • GET / (serve index.html)<br>• GET /health<br>• GET /api/today |
| **websocket.py** | Real-time communication | • WebSocket handling<br>• Message broadcasting<br>• Background tasks |
| **utils.py** | Helper functions | • Rate limiting<br>• Message sanitization |

### Frontend Components

| Component | Responsibility | Key Functions |
|-----------|---------------|---------------|
| **index.html** | Main chat interface | • Chat UI<br>• Message display<br>• Input form |
| **login.html** | Authentication page | • Login form<br>• Registration form<br>• Tab switching |
| **admin.html** | Admin dashboard | • Statistics display<br>• Message management<br>• User management |
| **script.js** | Frontend logic | • WebSocket connection<br>• API calls<br>• UI updates<br>• Auth state management |
| **styles.css** | Styling | • Dark theme<br>• Neon green accents<br>• Responsive design |

## Background Tasks

### 1. Midnight Clear Task
- **Function**: `midnight_clear_task()` in `websocket.py`
- **Purpose**: Clear messages at midnight every day
- **How it works**:
  1. Runs in infinite loop
  2. Checks if it's a new day (after midnight)
  3. Deletes messages from previous day
  4. Broadcasts system message to all connected clients
  5. Sleeps for 60 seconds, then repeats

### 2. Keep Alive Task
- **Function**: `keep_alive_task()` in `websocket.py`
- **Purpose**: Log heartbeat every 5 minutes
- **How it works**:
  1. Runs in infinite loop
  2. Logs current message count and connected clients
  3. Sleeps for 300 seconds (5 minutes), then repeats

## Security Features

1. **Password Hashing**: bcrypt with automatic truncation for 72-byte limit
2. **JWT Tokens**: 24-hour expiration, signed with SECRET_KEY
3. **Rate Limiting**: 25 messages per minute per user
4. **Input Validation**: Pydantic schemas sanitize all inputs
5. **CORS Protection**: Configurable allowed origins
6. **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
7. **Admin Authorization**: Separate admin routes with permission checks

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL
);
```

### Messages Table
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    user VARCHAR(50) NOT NULL,
    text VARCHAR(500) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    date_created VARCHAR(10) NOT NULL,  -- YYYY-MM-DD
    user_id INTEGER REFERENCES users(id)  -- Optional FK
);
```

## Environment Variables

| Variable | Purpose | Required | Default |
|----------|---------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes (production) | `sqlite:///./messages.db` |
| `SECRET_KEY` | JWT token signing key | Yes | `your-secret-key-change-this` |
| `ADMIN_PASSWORD` | Admin user password | Yes | None |
| `ADMIN_EMAIL` | Admin user email | No | `admin@rageroom.com` |
| `ALLOWED_ORIGINS` | CORS allowed origins | No | `*` |
| `DAILY_TOPIC` | Today's discussion topic | No | None |
| `DAILY_RULES` | Today's rules | No | None |

## API Endpoints Summary

### Public Endpoints
- `GET /` - Serve main chat page
- `GET /health` - Health check
- `GET /api/today` - Get today's topic
- `GET /api/messages` - Get message history
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `WebSocket /ws` - Real-time chat

### Protected Endpoints (Require JWT Token)
- `GET /api/auth/me` - Get current user info
- `GET /api/admin/stats` - Get statistics (admin only)
- `GET /api/admin/messages` - Get all messages (admin only)
- `POST /api/admin/topic` - Update daily topic (admin only)
- `DELETE /api/admin/message/{id}` - Delete message (admin only)
- `DELETE /api/admin/clear-messages` - Clear all messages (admin only)
- `GET /api/admin/users` - Get all users (admin only)
- `POST /api/admin/user/ban` - Ban/unban user (admin only)
