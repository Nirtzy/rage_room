# Rage Room

I decided to build an anonymous chat application where people can vent about daily frustrations without any permanent record. The idea is simple - you get a random nickname, chat about whatever's bothering you today, and everything gets wiped at midnight. It's like a digital rage room where you can let off steam anonymously.

## What I Built

The core concept is a real-time chat room that resets daily. Users can either chat anonymously with a randomly generated nickname that expires after 10 minutes, or they can register an account if they want a persistent identity. There's also an admin dashboard for managing the application.

The app uses WebSockets for real-time messaging, so when someone types a message, everyone sees it immediately. Messages are stored in a PostgreSQL database during the day, but there's a background task that clears everything at midnight to start fresh.

## Features

The anonymous chat is the main feature. Users get assigned a random nickname when they visit, and that nickname lasts for 10 minutes before expiring. This prevents people from camping on a single identity while still giving them enough time to have a conversation.

I added user authentication because some people might want to have accounts. Users can register with an email and password, and there's JWT-based authentication for secure login. The authentication is optional though - you can still use the app completely anonymously.

There's an admin panel for managing the application. Admins can view statistics, manage messages, update the daily topic, and ban users if needed. The admin user is created automatically on startup if you set the ADMIN_PASSWORD environment variable.

Rate limiting is built in to prevent spam. Users can send up to 25 messages per minute, and there's a 500 character limit per message. Input is sanitized to prevent XSS attacks.

## Tech Stack

Backend is FastAPI with Python. I chose FastAPI because it's fast, has great async support for WebSockets, and automatically generates API documentation. The database layer uses SQLAlchemy as the ORM, which makes it easy to work with PostgreSQL.

For authentication, I'm using JWT tokens with a 24-hour expiration. Passwords are hashed with bcrypt. The SECRET_KEY is used to sign tokens, so make sure to set a strong one in production.

The frontend is vanilla JavaScript - no frameworks. I kept it simple with separate CSS and JavaScript files for maintainability. The WebSocket connection handles real-time messaging, and localStorage stores authentication tokens.

## Running Locally

Install the dependencies first:

```
pip install -r requirements.txt
```

Then run the server:

```
uvicorn backend.main:app --reload
```

The app will be available at http://localhost:8000. It uses SQLite by default for local development, so you don't need to set up a database.

## Deployment

I'm deploying this on Render. You'll need to create a PostgreSQL database on Render and set up a few environment variables:

- DATABASE_URL - automatically set by Render when you link a database
- SECRET_KEY - a long random string for signing JWT tokens
- ADMIN_PASSWORD - the password for the admin account
- ADMIN_EMAIL - optional, defaults to admin@rageroom.com

The app automatically creates database tables on startup and sets up the admin user if ADMIN_PASSWORD is configured.

## Configuration

Most settings are in backend/config.py. You can adjust the rate limits, message length, connection limits, and CORS settings there. The daily topic can be set via the DAILY_TOPIC environment variable, or updated through the admin panel.

## Project Structure

The backend code is organized into separate modules. main.py is the entry point and sets up the FastAPI app. routes.py handles the public API endpoints, auth_routes.py handles login and registration, and admin_routes.py has the admin-only endpoints. websocket.py manages the real-time chat connections and background tasks.

The frontend is in the static directory. index.html is the main chat interface, login.html handles authentication, and admin.html is the admin dashboard. Each page has its own CSS and JavaScript files.

## API Endpoints

The main endpoints are:

- GET / - serves the chat interface
- GET /health - health check endpoint
- GET /api/today - returns today's topic and rules
- GET /api/messages - gets today's message history
- POST /api/auth/register - register a new user
- POST /api/auth/login - login and get JWT token
- GET /api/auth/me - get current user info
- WebSocket /ws - real-time chat connection

Admin endpoints are under /api/admin and require authentication with an admin account.

## Security Considerations

Rate limiting prevents spam and abuse. Input validation happens on both the frontend and backend using Pydantic schemas. SQL injection isn't a concern because we're using SQLAlchemy's ORM instead of raw SQL queries.

CORS is configured to allow requests from any origin by default, but you can restrict it to specific domains in production by setting the ALLOWED_ORIGINS environment variable.

The daily message clearing means there's no permanent record of conversations, which is by design. Messages are stored in the database during the day for persistence across page refreshes, but they get deleted at midnight.
