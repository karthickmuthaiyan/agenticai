FROM python:3.12-slim

# Prevent Python from writing .pyc files
# and make logs appear immediately.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Application directory
WORKDIR /app

# Install Python dependencies first
# to take advantage of Docker layer caching.
COPY requirements.txt .

# 1. Upgrade the active library
RUN pip install --no-cache-dir --upgrade "setuptools>=78.1.1"

# 2. Delete the dormant test `.whl` file that scanners flag
RUN find /usr/local/lib/python* -name "setuptools-*.whl" -delete

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# Copy the application
COPY . .

# Flask container port
EXPOSE 5000

# Start Flask
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]


