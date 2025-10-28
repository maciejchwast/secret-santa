FROM python:3.11-slim

WORKDIR /worker

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["celery", "-A", "app.tasks.mail_tasks.celery_app", "worker", "--loglevel=info"]
