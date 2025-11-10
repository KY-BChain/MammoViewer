FROM ubuntu:22.04

# Prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    wget \
    curl \
    xvfb \
    libgl1-mesa-glx \
    libglu1-mesa \
    libxrender1 \
    libxcursor1 \
    libxft2 \
    libxinerama1 \
    && rm -rf /var/lib/apt/lists/*

# Install 3D Slicer
RUN wget -q https://download.slicer.org/bitstream/1592769 -O Slicer.tar.gz && \
    tar -xzf Slicer.tar.gz -C /opt/ && \
    rm Slicer.tar.gz && \
    mv /opt/Slicer-* /opt/Slicer

# Set Slicer path
ENV SLICER_PATH=/opt/Slicer/Slicer

# Copy application files
COPY backend/requirements.txt /app/backend/requirements.txt

# Install Python dependencies
RUN pip3 install --no-cache-dir -r /app/backend/requirements.txt

# Copy the rest of the application
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/uploads /app/outputs /app/temp /app/logs /app/slicer_scripts

# Set permissions
RUN chmod -R 755 /app

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=backend/app.py
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# Start Xvfb and the application
CMD Xvfb :99 -screen 0 1024x768x24 & \
    cd backend && \
    python3 app.py