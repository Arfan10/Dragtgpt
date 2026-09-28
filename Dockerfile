# Base image with Python 3.10
FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies required by OpenCascade and graphics libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglx-mesa0 \
    libglu1-mesa \
    libgomp1 \
    libxrender1 \
    libxext6 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirement definition and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code and directories
COPY . /app/

# Create runtime folders for uploads and generated outputs
RUN mkdir -p /app/uploads /app/output

# Default port exposure for FastAPI
EXPOSE 8000

# Default command
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]