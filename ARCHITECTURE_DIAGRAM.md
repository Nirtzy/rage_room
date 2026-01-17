# 🎨 Rage Room - Visual Architecture Diagrams

## System Overview

```mermaid
graph TB
    subgraph "Client Layer"
        A[index.html<br/>Main Chat] 
        B[login.html<br/>Auth Page]
        C[admin.html<br/>Admin Dashboard]
        D[script.js<br/>Frontend Logic]
    end
    
    subgraph "FastAPI Server"
        E[main.py<br/>App Entry Point]
        F[routes.py<br/>Public Routes]
        G[auth_routes.py<br/>Auth Routes]
        H[admin_routes.py<br/>Admin Routes]
        I[websocket.py<br/>WebSocket Handler]
        J[auth.py<br/>JWT & Password]
        K[database.py<br/>DB Connection]
        L[models.py<br/>Data Models]
    end
    
    subgraph "Database"
        M[(PostgreSQL<br/>users table)]
        N[(PostgreSQL<br/>messages table)]
    end
    
    A --> D
    B --> D
    C --> D
    D -->|HTTP/WS| E
    E --> F
    E --> G
    E --> H
    E -->|WebSocket| I
    G --> J
    H --> J
    I --> K
    F --> K
    G --> K
    H --> K
    J --> K
    K --> L
    L --> M
    L --> N
```

## Authentication Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as Auth API
    participant DB as Database
    participant J as JWT Service
    
    Note over U,J: Registration Flow
    U->>F: Fill registration form
    F->>A: POST /api/auth/register
    A->>DB: Check email exists?
    DB-->>A: No
    A->>J: Hash password (bcrypt)
    J-->>A: Hashed password
    A->>DB: Create User
    DB-->>A: User created
    A-->>F: 201 Created
    F-->>U: Show success
    
    Note over U,J: Login Flow
    U->>F: Fill login form
    F->>A: POST /api/auth/login
    A->>DB: Find user by email
    DB-->>A: User found
    A->>J: Verify password
    J-->>A: Valid
    A->>J: Create JWT token
    J-->>A: Token
    A-->>F: Return token
    F->>F: Save to localStorage
    F->>A: GET /api/auth/me (with token)
    A->>J: Verify token
    J-->>A: Valid, user_id
    A->>DB: Get user by id
    DB-->>A: User data
    A-->>F: User info
    F-->>U: Redirect to chat/admin
```

## Chat Message Flow (WebSocket)

```mermaid
sequenceDiagram
    participant U1 as User 1
    participant U2 as User 2
    participant F as Frontend
    participant WS as WebSocket Handler
    participant DB as Database
    participant BC as Broadcast
    
    U1->>F: Type message
    F->>WS: WebSocket.send()
    WS->>WS: Validate message
    WS->>WS: Check rate limit
    WS->>DB: Save message
    DB-->>WS: Message saved
    WS->>BC: Broadcast to all
    BC->>F: Send to User 1
    BC->>F: Send to User 2
    F->>U1: Display own message
    F->>U2: Display User 1's message
```

## Admin Dashboard Flow

```mermaid
sequenceDiagram
    participant A as Admin
    participant F as Frontend
    participant API as Admin API
    participant Auth as Auth Service
    participant DB as Database
    
    A->>F: Open admin.html
    F->>F: Check localStorage token
    F->>API: GET /api/auth/me
    API->>Auth: Verify JWT token
    Auth-->>API: Valid, user_id
    API->>DB: Get user
    DB-->>API: User (is_admin=true)
    API-->>F: User data
    F->>API: GET /api/admin/stats
    API->>Auth: Verify admin
    Auth-->>API: Authorized
    API->>DB: Query statistics
    DB-->>API: Stats data
    API-->>F: Statistics
    F->>API: GET /api/admin/messages
    API->>DB: Query messages
    DB-->>API: Messages
    API-->>F: Messages list
    F->>A: Display dashboard
```

## Database Schema

```mermaid
erDiagram
    USERS ||--o{ MESSAGES : "optional"
    
    USERS {
        int id PK
        string email UK
        string username UK
        string hashed_password
        boolean is_active
        boolean is_admin
        datetime created_at
    }
    
    MESSAGES {
        int id PK
        string user
        string text
        datetime timestamp
        string date_created
        int user_id FK
    }
```

## Component Interaction

```mermaid
graph LR
    subgraph "Request Flow"
        A[HTTP Request] --> B{CORS Check}
        B -->|Allowed| C{Route Match}
        C -->|/api/auth/*| D[auth_routes]
        C -->|/api/admin/*| E[admin_routes]
        C -->|/api/*| F[routes]
        C -->|/ws| G[websocket]
        D --> H[auth.py]
        E --> H
        H --> I[database.py]
        F --> I
        G --> I
        I --> J[(PostgreSQL)]
    end
    
    subgraph "Response Flow"
        J --> I
        I --> K[models.py]
        K --> L[schemas.py]
        L --> M[Response]
    end
```

## Background Tasks

```mermaid
graph TD
    A[Server Startup] --> B[Start Background Tasks]
    B --> C[midnight_clear_task]
    B --> D[keep_alive_task]
    
    C --> E{Is it midnight?}
    E -->|No| F[Sleep 60s]
    F --> E
    E -->|Yes| G[Delete old messages]
    G --> H[Broadcast system message]
    H --> F
    
    D --> I[Log heartbeat]
    I --> J[Sleep 300s]
    J --> I
```

## Security Layers

```mermaid
graph TD
    A[Incoming Request] --> B[CORS Middleware]
    B --> C{Has Auth Token?}
    C -->|Yes| D[JWT Verification]
    C -->|No| E{Public Route?}
    E -->|Yes| F[Process Request]
    E -->|No| G[401 Unauthorized]
    D --> H{Token Valid?}
    H -->|Yes| I{Admin Route?}
    H -->|No| G
    I -->|Yes| J{Is Admin?}
    I -->|No| F
    J -->|Yes| F
    J -->|No| K[403 Forbidden]
    F --> L[Input Validation]
    L --> M[Rate Limiting]
    M --> N[Process Request]
```

## File Structure

```mermaid
graph TD
    A[rage_room/] --> B[backend/]
    A --> C[static/]
    A --> D[requirements.txt]
    
    B --> E[main.py]
    B --> F[config.py]
    B --> G[database.py]
    B --> H[models.py]
    B --> I[schemas.py]
    B --> J[auth.py]
    B --> K[auth_routes.py]
    B --> L[admin_routes.py]
    B --> M[routes.py]
    B --> N[websocket.py]
    B --> O[utils.py]
    
    C --> P[index.html]
    C --> Q[login.html]
    C --> R[admin.html]
    C --> S[script.js]
    C --> T[styles.css]
    
    E --> F
    E --> G
    E --> H
    E --> I
    E --> J
    E --> K
    E --> L
    E --> M
    E --> N
```

---

