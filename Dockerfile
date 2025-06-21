FROM python:3.10-slim

WORKDIR /app

# pip আপডেট করুন
RUN pip install --upgrade pip

# প্রথমে numpy আলাদাভাবে ইনস্টল করুন
RUN pip install numpy==1.26.4

# বাকি প্যাকেজেস
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ai_intrigation/pipeline_lg.joblib /app/ai_intrigation/pipeline_lg.joblib
COPY . .


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]



# FROM python:3.10-slim

# # Set working directory
# WORKDIR /app

# # Install system dependencies needed for mysqlclient
# RUN apt-get update && apt-get install -y \
#     gcc \
#     default-libmysqlclient-dev \
#     pkg-config \
#     && apt-get clean

# # Install Python dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy project files
# COPY . .
# COPY ai_intrigation/model.joblib /app/ai_intrigation/model.joblib
# # Collect static files (optional)
# RUN python manage.py collectstatic --noinput

# # Run with Daphne for WebSocket support
# CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "chat_system.asgi:application"]
