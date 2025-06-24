FROM python:3.10-slim

# Set working directory
WORKDIR /app

# ✅ System-level dependencies to build mysqlclient
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmariadb-dev \
    libssl-dev \
    default-libmysqlclient-dev \
    libpq-dev \
    pkg-config \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ✅ Install pip build tools
RUN pip install --upgrade pip setuptools wheel

# ✅ Numpy fix (if needed)
RUN pip install numpy==1.26.4

# ✅ Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy other files
COPY ai_intrigation/pipeline_lg.joblib /app/ai_intrigation/pipeline_lg.joblib
COPY . .

# ✅ Run the app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
