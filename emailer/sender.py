import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from config.settings import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self, to_email: Optional[str] = None):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.to_email = to_email or settings.to_email
        
        self.env = Environment(loader=FileSystemLoader("emailer/templates"))
        self.template = self.env.get_template("digest.html")

    def send_digest(self, jobs: list):
        if not all([self.smtp_user, self.smtp_password, self.to_email]):
            logger.warning("Email credentials not configured. Skipping email delivery.")
            return

        html_content = self.template.render(
            jobs=jobs,
            date=datetime.now().strftime("%B %d, %Y")
        )

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Job Digest - {datetime.now().strftime('%Y-%m-%d')}"
        msg["From"] = settings.smtp_user
        msg["To"] = self.to_email

        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
                logger.info(f"Email digest sent to {self.to_email}")
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
