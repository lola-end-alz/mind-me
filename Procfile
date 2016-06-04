web: gunicorn app:app
worker: python worker.py
scheduler: rqscheduler -i 5 --url $REDIS_URL