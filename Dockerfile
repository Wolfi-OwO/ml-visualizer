# Multi-stage Dockerfile for DSAI Webapp
# Optimized for production deployment with minimal image size

# ============================================================================
# Stage 1: Builder - Install dependencies
# ============================================================================
FROM python:3.12-slim AS builder
ARG APP_VERSION=1.0.0

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Stage 2: Runtime - Minimal production image
# ============================================================================
FROM python:3.12-slim
ARG APP_VERSION=1.0.0

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    STREAMLIT_SERVER_PORT=8080 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_RUN_ON_SAVE=false \
    ENVIRONMENT_NAME=production \
    APP_VERSION=${APP_VERSION}

# Metadata
LABEL app.version=${APP_VERSION}

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Persist application version inside the image
RUN echo "${APP_VERSION}" > /app/VERSION && chown appuser:appuser /app/VERSION

# Copy application files
COPY --chown=appuser:appuser src/pages ./src/pages
COPY --chown=appuser:appuser src/tests ./src/tests
COPY --chown=appuser:appuser src/styles ./src/styles
COPY --chown=appuser:appuser src/utils ./src/utils
COPY --chown=appuser:appuser src/app.py ./src/app.py

# Create .streamlit config directory
RUN mkdir -p /app/.streamlit && chown -R appuser:appuser /app/.streamlit

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8080/_stcore/health || exit 1

# Set stop signal
STOPSIGNAL SIGTERM

# Run the application
ENTRYPOINT ["streamlit", "run", "./src/app.py", \
     "--server.port=8080", \
     "--server.address=0.0.0.0", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=true", \
     "--server.maxUploadSize=10"]
