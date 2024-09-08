import dramatiq
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from products.utils import create_email_html

logger = logging.getLogger(__name__)

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "murattestemail@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "murattestemail1234")


def send_email(subject: str, to_email: str, body_html: str) -> None:
    """Send an email using SMTP with both plain text and HTML."""
    msg = MIMEMultipart("alternative")
    msg["From"] = SMTP_USERNAME
    msg["To"] = to_email
    msg["Subject"] = subject

    # Attach the HTML version
    msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, to_email, msg.as_string())
        logger.info(f"Email sent: {subject} to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}. Error: {e}")
        raise e


@dramatiq.actor(
    max_retries=int(os.getenv("DRAMATIQ_TASK_MAX_RETRIES", 5)),
    time_limit=int(os.getenv("DRAMATIQ_TASK_TIME_LIMIT_MS", 30 * 60000)),
    max_age=int(os.getenv("DRAMATIQ_TASK_MAX_AGE_MS", 3 * 60 * 60 * 1000)),
)
def send_notification(notification_data: dict) -> None:
    """
    Task to send a notification email about the upload status.
    """

    user_email = notification_data["user_email"]
    user_name = notification_data["user_name"]
    admin_email = notification_data["admin_email"]
    file_name = notification_data["file_name"]
    existing_product_ids = notification_data.get("existing_product_ids", [])
    problematic_product_ids = notification_data.get("problematic_product_ids", [])
    product = notification_data.get("product", {})
    status = notification_data.get("status", "notify_failure")

    if not admin_email:
        logger.error("Admin email is missing. Notification cannot be sent.")
        return

    subject = "Product Upload Successful" if status == "notify_success" else "Product Upload Failed"

    # Generate HTML version of the email using the utility function
    html_message = create_email_html(subject, user_name, user_email, file_name, product, existing_product_ids, problematic_product_ids, status)

    send_email(subject, admin_email, html_message)
