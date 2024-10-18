# Dockerfile
FROM python:3.9-slim-buster

# Set environment variables for optimal behavior and security
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=src/app:create_app

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt

# TEMP
RUN apt-get update && apt-get install -y curl

# Copy the application source code
COPY src /app/src
COPY config /app/config

# Creates a non-root user and grants permission to access /app
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Expose the internal application port
EXPOSE 5000

# Use Flask's built-in development server for simplicity
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]