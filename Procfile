web: gunicorn app:app
worker: celery -A app.celery worker -l info