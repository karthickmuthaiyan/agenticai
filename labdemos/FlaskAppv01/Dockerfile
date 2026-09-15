# ==========================================
# Stage 1: Build & Dependency Isolation
# ==========================================
FROM python:3.13-slim AS builder

WORKDIR /app

# Install system build dependencies securely if required (e.g., compilers)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install Python dependencies first
# to take advantage of Docker layer caching.
#COPY requirements.txt .

# 1. Upgrade the active library
#RUN pip install --no-cache-dir --upgrade "setuptools>=78.1.1"

# 2. Delete the dormant test `.whl` file that scanners flag
#RUN find /usr/local/lib/python* -name "setuptools-*.whl" -delete

#RUN pip install --no-cache-dir --upgrade pip \
#    && pip install --no-cache-dir -r requirements.txt


# Copy only requirements to leverage Docker layer caching
COPY requirements.txt .

# Securely install dependencies into a localized directory (or virtual env)
# Note: If pulling from private registries, leverage --mount=type=secret
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir --user -r requirements.txt


# ==========================================
# Stage 2: Final Secure Runtime Image
# ==========================================
FROM python:3.13-slim AS runner

# Application directory
WORKDIR /app

# Prevent Python from writing .pyc files
# and make logs appear immediately.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:$PATH"

# 1. Create a dedicated non-root user and group
RUN groupadd -r appgroup && useradd -r -g appgroup -m appuser

# 2. Copy installed dependencies from the builder stage
COPY --from=builder /root/.local /home/appuser/.local

# 3. Copy application source code and adjust ownership
COPY --chown=appuser:appgroup . .

# 4. Drop root privileges completely
USER appuser

# Flask container port
EXPOSE 5000

# Start Flask
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]


