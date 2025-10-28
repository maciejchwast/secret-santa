from __future__ import annotations

from typing import Any, Dict

import requests

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
    response = requests.post(
        f"{settings.mailgun_api_base_url}/{settings.mailgun_domain}/messages",
        auth=("api", settings.mailgun_api_key),
        data={
            "from": settings.mailgun_sender,
            "to": [to_email],
            "subject": subject,
            "html": html_body,
        },
    )
    response.raise_for_status()
