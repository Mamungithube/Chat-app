# 🗨️ Django Channels Chat App with JWT Authentication

A real-time chat application built with Django Channels and secured using JSON Web Token (JWT) authentication.

---

## 🚀 Features

- 🔐 JWT Authentication for secure access
- 💬 Real-time messaging using WebSockets (via Django Channels)
- 👥 User registration and login
- 📡 WebSocket connection authenticated via JWT
- 🧪 API endpoints for authentication and user operations
- 📦 Optional Postman/cURL support for testing

---

## 🛠️ Tech Stack

- **Backend**: Django, Django REST Framework
- **Real-time**: Django Channels, WebSockets, Redis
- **Authentication**: JWT (djangorestframework-simplejwt)

---

## ⚙️ Setup Instructions
api setup
- live link ----> https://chat-app-9tq4.onrender.com
- user all api https://chat-app-9tq4.onrender.com/authontication/user_all/
- register api https://chat-app-9tq4.onrender.com/authontication/register/
- resend api https://chat-app-9tq4.onrender.com/authontication/resend_otp/
- verify_otp api https://chat-app-9tq4.onrender.com/authontication/verify_otp/
- login api https://chat-app-9tq4.onrender.com/authontication/login/
- logout api https://chat-app-9tq4.onrender.com/authontication/logout/
- refesh token api https://chat-app-9tq4.onrender.com/authontication/token/refresh/

- chat channal api ws://localhost:8000/ws/chat/room1/?token=access token name when login
- Render not supportet web shocket in Free plan But locally connect and work...
### 1. Clone the Repository

```bash
git clone https://github.com/Mamungithube/Chat-app.git



