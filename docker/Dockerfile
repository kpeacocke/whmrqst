# Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=questbetween.settings \
    PYTHONPATH=/app/src

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir -r /app/requirements.txt gunicorn==23.0.0

COPY manage.py /app/manage.py
COPY src /app/src

RUN adduser -u 5678 --disabled-password --gecos "" appuser \
    && chown -R appuser /app \
    && python manage.py collectstatic --noinput \
    && chown -R appuser /app/staticfiles
USER 5678:5678

EXPOSE 8000

CMD ["gunicorn", "questbetween.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
