from __future__ import annotations

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..config import get_settings

settings = get_settings()

template_env = Environment(
    loader=FileSystemLoader("backend/app/templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


def render_assignment_email(context: Dict[str, Any]) -> str:
    template = template_env.get_template("assignment_email.html")
    return template.render(**context)


def send_email(to_email: str, subject: str, html_body: str) -> None:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.smtp_sender
    message["To"] = to_email
    message.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port) as server:
        server.login(settings.smtp_username, settings.smtp_password)
        server.sendmail(settings.smtp_sender, [to_email], message.as_string())
