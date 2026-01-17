# 📚 Rage Room - Learning Guide

This guide explains the key concepts and technologies you need to understand to modify and extend this project.

## Table of Contents

1. [Core Technologies](#core-technologies)
2. [FastAPI Fundamentals](#fastapi-fundamentals)
3. [Database & ORM (SQLAlchemy)](#database--orm-sqlalchemy)
4. [Authentication & Security](#authentication--security)
5. [WebSockets & Real-time Communication](#websockets--real-time-communication)
6. [Frontend Development](#frontend-development)
7. [Project-Specific Concepts](#project-specific-concepts)
8. [Common Modifications](#common-modifications)

---

## Core Technologies

### 1. Python 3.11+
**Why it's used**: Backend language for the FastAPI server

**Key concepts to learn**:
- **Async/Await**: Used throughout for non-blocking operations
  ```python
  async def my_function():
      result = await some_async_operation()
      return result
  ```
- **Type Hints**: Used for better code documentation and IDE support
  ```python
  def get_user(user_id: int) -> User:
      return db.query(User).filter(User.id == user_id).first()
  ```
- **Context Managers**: Used for database sessions and app lifespan
  ```python
  with SessionLocal() as db:
      # Use database session
      pass
  ```

**Resources**:
- [Python Async/Await Tutorial](https://realpython.com/async-io-python/)
- [Python Type Hints Guide](https://docs.python.org/3/library/typing.html)

---

### 2. FastAPI Framework
**Why it's used**: Modern, fast web framework for building APIs

**Key concepts to learn**:

#### **Routers & Endpoints**
```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register")
async def register(user_data: UserCreate):
    # Handle registration
    return new_user
```

**What to learn**:
- How to create routes (`@router.get`, `@router.post`, etc.)
- Path parameters (`/users/{user_id}`)
- Query parameters (`?skip=0&limit=10`)
- Request bodies (Pydantic models)
- Response models

#### **Dependency Injection**
```python
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/users")
async def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

**What to learn**:
- How `Depends()` works
- Creating reusable dependencies
- Dependency chains

#### **Middleware**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
)
```

**What to learn**:
- What middleware does (runs before/after requests)
- CORS (Cross-Origin Resource Sharing)
- Custom middleware creation

**Resources**:
- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)

---

## Database & ORM (SQLAlchemy)

### SQLAlchemy Basics
**Why it's used**: Object-Relational Mapping (ORM) to interact with PostgreSQL

**Key concepts to learn**:

#### **Models (Database Tables)**
```python
from sqlalchemy import Column, Integer, String
from backend.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
```

**What to learn**:
- Column types (`Integer`, `String`, `Boolean`, `DateTime`)
- Constraints (`unique=True`, `nullable=False`)
- Primary keys and foreign keys
- Relationships (one-to-many, many-to-many)

#### **Querying Data**
```python
# Get all users
users = db.query(User).all()

# Get user by email
user = db.query(User).filter(User.email == email).first()

# Get users with conditions
active_users = db.query(User).filter(User.is_active == True).all()

# Count
user_count = db.query(User).count()
```

**What to learn**:
- `db.query()` - Start a query
- `.filter()` - Add WHERE conditions
- `.first()` - Get first result (or None)
- `.all()` - Get all results
- `.count()` - Count results
- `.order_by()` - Sort results
- `.limit()` / `.offset()` - Pagination

#### **Creating/Updating Data**
```python
# Create new user
new_user = User(
    email="user@example.com",
    username="newuser",
    hashed_password=hashed_pwd
)
db.add(new_user)
db.commit()
db.refresh(new_user)  # Get auto-generated ID

# Update user
user = db.query(User).filter(User.id == user_id).first()
user.is_active = False
db.commit()

# Delete user
db.delete(user)
db.commit()
```

**What to learn**:
- `db.add()` - Add new object
- `db.commit()` - Save changes
- `db.rollback()` - Undo changes
- `db.refresh()` - Reload from database
- `db.delete()` - Delete object

**Resources**:
- [SQLAlchemy Core Tutorial](https://docs.sqlalchemy.org/en/14/tutorial/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/14/orm/tutorial.html)

---

## Authentication & Security

### JWT (JSON Web Tokens)
**Why it's used**: Stateless authentication - server doesn't need to store sessions

**How it works**:
1. User logs in with email/password
2. Server creates a JWT token containing user ID
3. Server signs token with SECRET_KEY
4. Client stores token (localStorage)
5. Client sends token with each request
6. Server verifies token and extracts user ID

**Key concepts**:
```python
# Create token
from jose import jwt
token = jwt.encode({"sub": user_id}, SECRET_KEY, algorithm="HS256")

# Decode token
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
user_id = payload.get("sub")
```

**What to learn**:
- Token structure (header.payload.signature)
- Token expiration
- Token signing and verification
- Bearer token authentication

### Password Hashing (bcrypt)
**Why it's used**: Never store plain text passwords

**How it works**:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

# Hash password
hashed = pwd_context.hash("my_password")

# Verify password
is_valid = pwd_context.verify("my_password", hashed)
```

**Key points**:
- bcrypt automatically adds salt
- Same password = different hash each time
- One-way function (can't reverse)
- 72-byte password limit (handled in code)

**Resources**:
- [JWT.io - JWT Debugger](https://jwt.io/)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)

---

## WebSockets & Real-time Communication

### WebSocket Basics
**Why it's used**: Two-way communication for real-time chat (better than polling)

**How it works**:
```
Client                    Server
  │                         │
  ├─── WebSocket.connect() ──>│
  │<─── Accept connection ───┤
  │                         │
  ├─── Send message ────────>│
  │                         │ (Process & save)
  │<─── Broadcast to all ───┤
  │                         │
  │<─── Other user's msg ────┤
  │                         │
```

**Key concepts**:

#### **Server Side (FastAPI)**
```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accept connection
    
    while True:
        data = await websocket.receive_text()  # Receive message
        # Process message
        await websocket.send_text(response)  # Send response
```

#### **Client Side (JavaScript)**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
    console.log('Connected');
};

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    // Display message
};

ws.send(JSON.stringify({
    user: 'username',
    text: 'Hello!'
}));
```

**What to learn**:
- WebSocket protocol vs HTTP
- Connection lifecycle
- Message broadcasting
- Error handling and reconnection
- Connection management (tracking connected clients)

**Resources**:
- [MDN WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)

---

## Frontend Development

### JavaScript (ES6+)
**Key concepts used in this project**:

#### **Async/Await**
```javascript
async function login(email, password) {
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Login failed:', error);
    }
}
```

#### **Fetch API**
```javascript
// GET request
const response = await fetch('/api/users');
const users = await response.json();

// POST request
const response = await fetch('/api/users', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: 'John' })
});
```

#### **localStorage**
```javascript
// Save
localStorage.setItem('access_token', token);
localStorage.setItem('user', JSON.stringify(userData));

// Read
const token = localStorage.getItem('access_token');
const user = JSON.parse(localStorage.getItem('user'));

// Remove
localStorage.removeItem('access_token');
```

**What to learn**:
- Promises and async/await
- Fetch API for HTTP requests
- DOM manipulation
- Event handling
- localStorage for client-side storage

### HTML/CSS
**Key concepts**:
- Semantic HTML structure
- CSS selectors and styling
- Flexbox/Grid for layout
- Responsive design

**Resources**:
- [MDN JavaScript Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)
- [JavaScript.info](https://javascript.info/)

---

## Project-Specific Concepts

### 1. Pydantic Schemas
**Purpose**: Validate and sanitize request/response data

```python
from pydantic import BaseModel, Field, field_validator

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    
    @field_validator('username')
    @classmethod
    def sanitize_username(cls, v: str) -> str:
        return v.strip()
```

**What to learn**:
- Field validation
- Custom validators
- Type conversion
- Error messages

### 2. Rate Limiting
**Purpose**: Prevent spam (25 messages per minute per user)

```python
from collections import deque
import time

user_message_timestamps: Dict[str, deque] = {}

def is_rate_limited(user: str) -> bool:
    now = time.time()
    # Remove timestamps older than 1 minute
    # Check if user exceeded limit
    return len(timestamps) >= MAX_MESSAGES_PER_MINUTE
```

**What to learn**:
- Time-based rate limiting
- Sliding window algorithm
- Per-user tracking

### 3. Background Tasks
**Purpose**: Run periodic tasks (midnight clearing, heartbeat)

```python
async def midnight_clear_task():
    while True:
        now = datetime.now()
        if now.time() >= time(0, 0):  # Midnight
            # Clear messages
            pass
        await asyncio.sleep(60)  # Check every minute
```

**What to learn**:
- Async infinite loops
- Task scheduling
- Background task management

---

## Common Modifications

### Adding a New API Endpoint

1. **Create the route function**:
```python
# In routes.py or new file
@router.get("/api/my-endpoint")
async def my_endpoint(db: Session = Depends(get_db)):
    return {"message": "Hello"}
```

2. **Register the router** (if new file):
```python
# In main.py
from backend.my_routes import router as my_router
app.include_router(my_router)
```

3. **Add frontend call** (if needed):
```javascript
const response = await fetch('/api/my-endpoint');
const data = await response.json();
```

### Adding a New Database Table

1. **Create the model**:
```python
# In models.py
class MyModel(Base):
    __tablename__ = "my_table"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
```

2. **Create the schema**:
```python
# In schemas.py
class MyModelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
```

3. **The table is created automatically** on next startup (via `init_db()`)

### Adding Authentication to an Endpoint

```python
from backend.auth import get_current_user

@router.get("/api/protected")
async def protected_endpoint(
    current_user: User = Depends(get_current_user)
):
    return {"user": current_user.username}
```

### Adding Admin-Only Endpoint

```python
from backend.auth import get_current_admin_user

@router.delete("/api/admin/delete-all")
async def delete_all(
    current_user: User = Depends(get_current_admin_user)
):
    # Only admins can access this
    return {"message": "Deleted"}
```

### Modifying WebSocket Behavior

```python
# In websocket.py
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Add custom logic here
    # e.g., send welcome message
    await websocket.send_text(json.dumps({
        "user": "System",
        "text": "Welcome!",
        "timestamp": datetime.now().isoformat()
    }))
    
    # Continue with existing logic...
```

### Adding Environment Variables

1. **Add to config.py**:
```python
MY_NEW_VAR = os.getenv("MY_NEW_VAR", "default_value")
```

2. **Use in code**:
```python
from backend.config import MY_NEW_VAR
```

3. **Set in Render**: Add to Environment Variables in dashboard

---

## Learning Path Recommendation

### Beginner Level
1. ✅ Understand Python basics (variables, functions, classes)
2. ✅ Learn FastAPI basics (routes, requests, responses)
3. ✅ Understand SQLAlchemy basics (models, queries)
4. ✅ Learn JavaScript basics (variables, functions, async/await)

### Intermediate Level
1. ✅ Master FastAPI (dependencies, middleware, WebSockets)
2. ✅ Deep dive into SQLAlchemy (relationships, transactions)
3. ✅ Understand JWT authentication
4. ✅ Learn WebSocket programming

### Advanced Level
1. ✅ Database optimization (indexes, query optimization)
2. ✅ Security best practices (input validation, SQL injection prevention)
3. ✅ Error handling and logging
4. ✅ Testing (unit tests, integration tests)

---

## Useful Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [MDN Web Docs](https://developer.mozilla.org/)

### Tutorials
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Real Python - Async Python](https://realpython.com/async-io-python/)
- [JavaScript.info](https://javascript.info/)

### Tools
- [Postman](https://www.postman.com/) - API testing
- [pgAdmin](https://www.pgadmin.org/) - PostgreSQL GUI
- [JWT.io](https://jwt.io/) - JWT debugger

---

## Tips for Modifying This Project

1. **Start Small**: Make small changes and test frequently
2. **Read the Logs**: Check Render logs to see what's happening
3. **Test Locally First**: Use `uvicorn backend.main:app --reload` for development
4. **Use Type Hints**: They help catch errors early
5. **Follow the Patterns**: Look at existing code to see how things are done
6. **Check Dependencies**: Make sure new packages are in `requirements.txt`
7. **Database Migrations**: For schema changes, you may need to manually update the database
8. **Environment Variables**: Remember to set them in Render dashboard

---

## Getting Help

- **FastAPI Issues**: Check [FastAPI GitHub](https://github.com/tiangolo/fastapi)
- **SQLAlchemy Issues**: Check [SQLAlchemy GitHub](https://github.com/sqlalchemy/sqlalchemy)
- **Stack Overflow**: Search for specific error messages
- **Documentation**: Always check official docs first

---

**Happy Coding! 🚀**
