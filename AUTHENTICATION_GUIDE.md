# 🔥 Rage Room - Authentication & Admin System

## ✅ What I've Added

I've successfully implemented a complete authentication and admin system for your Rage Room application! Here's what's new:

---

## 🎯 New Features

### 1. **User Authentication (JWT-based)**
- ✅ User registration with email and password
- ✅ Secure login with JWT tokens
- ✅ Password hashing with bcrypt
- ✅ Token-based authentication (24-hour expiration)
- ✅ Optional authentication (users can still chat anonymously)

### 2. **Admin Dashboard**
- ✅ Protected admin panel at `/static/admin.html`
- ✅ Real-time statistics (total users, messages, today's messages)
- ✅ Update daily topics via UI (no more manual env var changes!)
- ✅ View and delete individual messages
- ✅ Clear all messages at once
- ✅ View all registered users
- ✅ Ban/unban users

### 3. **Three User Types**
1. **Anonymous Users** - Can chat without registration (like before)
2. **Registered Users** - Can create accounts and login
3. **Admin User** - Full control over the application

---

## 📁 New Files Created

### Backend:
- `backend/auth.py` - Authentication utilities (JWT, password hashing)
- `backend/auth_routes.py` - Login/register API endpoints
- `backend/admin_routes.py` - Admin-only API endpoints
- `backend/init_admin.py` - Script to manually create admin user

### Frontend:
- `static/login.html` - Login/register page
- `static/admin.html` - Admin dashboard

### Updated Files:
- `backend/models.py` - Added User model
- `backend/schemas.py` - Added auth schemas
- `backend/config.py` - Added JWT and admin config
- `backend/main.py` - Integrated auth routes, auto-creates admin user
- `backend/database.py` - Updated to include User model
- `static/index.html` - Added login/admin links
- `static/script.js` - Added auth support
- `requirements.txt` - Added auth dependencies

---

## 🚀 How to Use Locally

### 1. **Set Admin Password**
```bash
export ADMIN_PASSWORD="your-secure-password"
export SECRET_KEY="your-secret-jwt-key-change-this"
```

### 2. **Run the Server**
```bash
cd /Users/danilkarpov/PycharmProjects/rage_room
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uvicorn backend.main:app --reload
```

### 3. **Access the Application**
- **Main Chat**: http://localhost:8000/
- **Login/Register**: http://localhost:8000/static/login.html
- **Admin Dashboard**: http://localhost:8000/static/admin.html

### 4. **Login as Admin**
- Email: `admin@rageroom.com` (default, or set via ADMIN_EMAIL env var)
- Password: Whatever you set in ADMIN_PASSWORD

---

## 🌐 Deployment to Render

### 1. **Set Environment Variables in Render Dashboard**

Go to your Render web service → Environment → Add these variables:

```
ADMIN_PASSWORD=your-secure-admin-password-here
SECRET_KEY=your-random-secret-key-minimum-32-characters-long
ADMIN_EMAIL=your-email@example.com  (optional, defaults to admin@rageroom.com)
```

**Important**: 
- `SECRET_KEY` should be a long random string (at least 32 characters)
- `ADMIN_PASSWORD` should be strong and secure
- Generate a secret key with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

### 2. **Database Migration**

Your PostgreSQL database will automatically create the new `users` table on the next deploy. The admin user will be created automatically on startup if ADMIN_PASSWORD is set.

### 3. **Commit and Push**

```bash
git add .
git commit -m "Add authentication and admin system"
git push origin main
```

Render will automatically deploy the changes.

---

## 🔐 Security Features

✅ **Password Security**
- Passwords are hashed with bcrypt (industry standard)
- Never stored in plain text

✅ **JWT Tokens**
- Stateless authentication
- 24-hour expiration
- Secure token generation

✅ **Protected Routes**
- Admin routes require admin privileges
- User routes require authentication
- Automatic token validation

✅ **Rate Limiting**
- Existing message rate limits still apply
- Protection against spam

---

## 📊 Admin Dashboard Features

### Statistics Panel
- Total registered users
- Total messages (all time)
- Today's messages count

### Topic Management
- Set daily topic via UI
- Add optional rules/description
- Note: For persistent changes, still update env vars in Render

### Message Moderation
- View recent messages (up to 50)
- Delete individual messages
- Clear all messages with confirmation

### User Management (Ready for future)
- View all users
- Ban/unban users
- Admin users cannot be banned

---

## 🎨 User Experience

### For Anonymous Users:
- Nothing changes! Can still chat without registration
- Optional "Login/Register" link in header
- Nickname system works the same (10 minutes)

### For Registered Users:
- Can create account and login
- Username displayed in header
- Can access admin panel (if admin)
- Future: Could add profile, message history, etc.

### For Admin:
- Full control panel
- Set topics without touching code
- Moderate content in real-time
- View statistics

---

## 🛠️ API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout (client-side)

### Admin (Requires Admin Role)
- `GET /api/admin/stats` - Get application statistics
- `POST /api/admin/topic` - Update daily topic
- `DELETE /api/admin/message/{id}` - Delete a message
- `GET /api/admin/messages` - Get all messages
- `GET /api/admin/users` - Get all users
- `POST /api/admin/user/ban` - Ban/unban a user
- `DELETE /api/admin/clear-messages` - Clear all messages

---

## 🧪 Testing Locally

1. **Test Anonymous Chat** (works as before)
   - Go to http://localhost:8000/
   - Send messages without logging in

2. **Test Registration**
   - Click "Login/Register" in header
   - Create a new account
   - Login with your credentials

3. **Test Admin Login**
   - Login with admin credentials
   - Access admin dashboard
   - Try updating topic, viewing stats, etc.

---

## 🐛 Troubleshooting

### "Admin password not set"
- Make sure ADMIN_PASSWORD environment variable is set
- Restart the server after setting env vars

### "Authentication failed"
- Check if SECRET_KEY is set
- Make sure it's the same key used to generate the token

### "Access denied: Admin privileges required"
- Only the admin user can access /static/admin.html
- Make sure you're logged in with admin credentials

### Database errors
- Delete `messages.db` to reset local database
- On Render, database will auto-migrate

---

## 🚧 Future Enhancements (You Can Add)

- [ ] Email verification for new users
- [ ] Password reset functionality
- [ ] User profiles with avatars
- [ ] Message history for logged-in users
- [ ] Admin can assign moderator role
- [ ] Analytics dashboard (charts, graphs)
- [ ] Bulk user management
- [ ] Automated topic rotation
- [ ] User reputation system
- [ ] Notifications for admins

---

## 📝 Important Notes

1. **Anonymous chat still works** - Users don't need to register to use the app
2. **Admin user is auto-created** - Just set ADMIN_PASSWORD in environment
3. **PostgreSQL compatible** - All changes work with both SQLite and PostgreSQL
4. **No data loss** - Existing messages are preserved during migration
5. **Topic updates via UI** - But need env vars for persistence across restarts

---

## 🎉 You're All Set!

Your Rage Room now has:
✅ Secure user authentication
✅ Admin dashboard for easy management
✅ Topic updates via UI
✅ Message moderation
✅ User management
✅ All while keeping anonymous chat functional!

Just set the environment variables and deploy to Render!

