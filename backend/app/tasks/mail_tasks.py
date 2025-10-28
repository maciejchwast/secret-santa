from __future__ import annotations

from celery import Celery

from ..config import get_settings
from ..services import emailer

settings = get_settings()

celery_app = Celery(
    "secret_santa",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)


@celery_app.task
def send_assignment_email(to_email: str, subject: str, context: dict) -> None:
    body = emailer.render_assignment_email(context)
    emailer.send_email(to_email, subject, body)
