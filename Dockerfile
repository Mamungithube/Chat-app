# Dockerfile

# # Python base image
# FROM python:3.10-slim

# # Set work directory
# WORKDIR /app

# # Install dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy project files
# COPY . .

# # Collect static files (optional)
# RUN python manage.py collectstatic --noinput

# # Run server
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Dockerfile

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for mysqlclient
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && apt-get clean

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files (optional)
RUN python manage.py collectstatic --noinput

# Run with Daphne for WebSocket support
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "chat_system.asgi:application"]
