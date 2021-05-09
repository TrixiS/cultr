import aiosmtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader

from typing import Union, List
from pathlib import Path

from ..config import settings

jinja_env = Environment(loader=FileSystemLoader(
    Path(__file__).parent / "../email_templates"))


async def send_email(to: Union[str, List[str]], message):
    await aiosmtplib.send(
        message,
        sender=settings.EMAIL_USER,
        recipients=[to] if isinstance(to, str) else to,
        hostname=settings.EMAIL_HOST,
        username=settings.EMAIL_USER,
        password=settings.EMAIL_PASS,
        port=settings.EMAIL_PORT,
        start_tls=settings.EMAIL_PORT == 587,
        use_tls=settings.EMAIL_PORT == 465
    )


async def send_email_confirmation(to: Union[str, List[str]], confirm_url: str):
    message = MIMEMultipart("alternative")
    message["From"] = settings.EMAIL_USER
    message["To"] = to
    message["Subject"] = "Cultr Account Confirmation"

    template = jinja_env.get_template("account_confirmation.html")
    html = template.render(confirm_url=confirm_url)
    message_html = MIMEText(html, "html", "utf-8")
    message.attach(message_html)

    await send_email(to, message)
