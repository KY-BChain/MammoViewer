# MammoViewer Dockerfile
# Ubuntu-based container with Python, 3D Slicer, and dependencies

FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    SLICER_VERSION=5.4.0 \
    SLICER_URL=https://download.slicer.org/

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3-dev \
    wget \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libglu1-mesa \
    libpulse-mainloop-glib0 \
    xvfb \
    xauth \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy requirements first for better caching
COPY backend/requirements.txt /app/backend/requirements.txt

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r backend/requirements.txt

# Download and install 3D Slicer
# Note: This downloads a large file (~500MB). For production, consider:
# 1. Pre-downloading and adding to container
# 2. Using a multi-stage build
# 3. Creating a base image with Slicer pre-installed
RUN mkdir -p /opt/Slicer && \
    echo "Downloading 3D Slicer..." && \
    wget -q --show-progress \
    "https://download.slicer.org/bitstream/1539390" \
    -O /tmp/Slicer.tar.gz && \
    tar -xzf /tmp/Slicer.tar.gz -C /opt/ && \
    rm /tmp/Slicer.tar.gz && \
    ln -s /opt/Slicer-*/Slicer /opt/Slicer/Slicer

# Alternative: If Slicer is already downloaded locally
# COPY Slicer-5.4.0-linux-amd64.tar.gz /tmp/
# RUN tar -xzf /tmp/Slicer-5.4.0-linux-amd64.tar.gz -C /opt/ && \
#     rm /tmp/Slicer-5.4.0-linux-amd64.tar.gz && \
#     ln -s /opt/Slicer-*/Slicer /opt/Slicer/Slicer

# Copy application files
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/
COPY .env.example /app/.env.example

# Create necessary directories
RUN mkdir -p /app/uploads /app/outputs /app/temp /app/logs /app/slicer_scripts

# Set permissions
RUN chmod -R 755 /app

# Create a non-root user
RUN useradd -m -u 1000 mammoviewer && \
    chown -R mammoviewer:mammoviewer /app

# Switch to non-root user
USER mammoviewer

# Expose port
EXPOSE 5000

# Set environment variables
ENV SLICER_PATH=/opt/Slicer/Slicer \
    FLASK_APP=backend/app.py \
    PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run the application with Xvfb for headless Slicer
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 & export DISPLAY=:99 && python3 backend/app.py"]
