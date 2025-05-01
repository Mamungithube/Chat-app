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
#api setup
user all api http://127.0.0.1:8000/authontication/user_all/
register api http://127.0.0.1:8000/authontication/register/
resend api http://127.0.0.1:8000/authontication/resend_otp/
verify_otp api http://127.0.0.1:8000/authontication/verify_otp/
login api http://127.0.0.1:8000/authontication/login/
logout api http://127.0.0.1:8000/authontication/logout/
refesh token api http://127.0.0.1:8000/authontication/token/refresh/

chat channal api ws://localhost:8000/ws/chat/room1/?token=access token name when login
### 1. Clone the Repository

```bash
git clone https://github.com/Mamungithube/Chat-app.git
cd django-chat-jwt



