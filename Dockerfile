# Optimized Dockerfile for AndroidWorld with Genymotion Emulator Support
# This container can connect to Android emulators and run AndroidWorld tasks
# Updated with working, production-ready configuration and fast build optimization

FROM ubuntu:20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Environment variables for AndroidWorld Challenge
ENV GENYMOTION_USERNAME=""
ENV GENYMOTION_PASSWORD=""
ENV GENYMOTION_LICENSE_KEY=""
ENV DEFAULT_EPISODES=50
ENV DEFAULT_AGENT_TYPE=orchestrator
ENV DEFAULT_OUTPUT_FORMAT=json

# Install system dependencies in a single optimized layer
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    python3 \
    python3-pip \
    android-tools-adb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/apt

# Create working directory
WORKDIR /workspace

# Copy requirements file first for better layer caching
COPY requirements.txt /workspace/

# Install Python dependencies in a single layer with optimizations
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Create directories for logs and outputs
RUN mkdir -p /workspace/logs /workspace/outputs /workspace/models /workspace/scripts

# Copy utility scripts (if they exist)
COPY scripts/ /workspace/scripts/
RUN find /workspace/scripts -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true

# Set up ADB server startup
RUN echo '#!/bin/bash' > /usr/local/bin/adb-entrypoint.sh && \
    echo 'echo "Starting ADB server..."' >> /usr/local/bin/adb-entrypoint.sh && \
    echo 'adb start-server' >> /usr/local/bin/adb-entrypoint.sh && \
    echo 'echo "ADB server ready"' >> /usr/local/bin/adb-entrypoint.sh && \
    echo 'exec "$@"' >> /usr/local/bin/adb-entrypoint.sh && \
    chmod +x /usr/local/bin/adb-entrypoint.sh

# Create a non-root user for security
RUN useradd -m -s /bin/bash androiduser && \
    chown -R androiduser:androiduser /workspace

# Switch to non-root user
USER androiduser

# Expose ADB port and web server port
EXPOSE 5037 8080

# Set entrypoint to start ADB server and web server
ENTRYPOINT ["/usr/local/bin/adb-entrypoint.sh"]

# Default command - start the web server
CMD ["python3", "-m", "agents.web_server"]
