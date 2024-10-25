# Dockerfile
FROM python:3-slim

# Set environment variables for optimal behavior and security
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=src/app:create_app

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY src /app/src
COPY config /app/config
COPY scripts/db_seed.py /app/scripts/db_seed.py

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Command to run both the seeding script and the Flask server
CMD ["sh", "-c", "python /app/scripts/db_seed.py && flask run --host=0.0.0.0 --port=5000"]