import os

if os.environ['FLASK_ENV'] == 'development':
    client_id = int(os.environ['STRAVA_CLIENT_ID'])
    client_secret = os.environ['STRAVA_CLIENT_SECRET']
    url = 'http://localhost:5000/'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

elif os.environ['FLASK_ENV'] == 'development-live':
    client_id = int(os.environ['STRAVA_CLIENT_ID'])
    client_secret = os.environ['STRAVA_CLIENT_SECRET']
    url = 'https://https://bulk-update-dev.herokuapp.com/'
    # Celery:
    CELERY_BROKER_URL = os.environ.get('REDIS_URL')
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')
    # Redis:
    REDIS_URL = os.environ.get('REDIS_URL')
else:
    client_id = int(os.environ['STRAVA_CLIENT_ID'])
    client_secret = os.environ['STRAVA_CLIENT_SECRET']
    url = 'https://bulk-update-gear.herokuapp.com/'
    # Celery:
    CELERY_BROKER_URL = os.environ.get('REDIS_URL')
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')
    # Redis:
    REDIS_URL = os.environ.get('REDIS_URL')