# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3-slim

EXPOSE 5000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_APP=/app/src/run.py

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install pip requirements
COPY ../requirements.txt .
RUN python -m pip install --no-cache-dir  -r requirements.txt

COPY / /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Use Flask's built-in development server
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
