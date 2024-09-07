import dramatiq
import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


logger = logging.getLogger(__name__)

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "murattestemail@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "murattestemail1234")


def send_email(subject: str, to_email: str, body: str) -> None:
    """Send an email using SMTP."""
    msg = MIMEMultipart()
    msg["From"] = SMTP_USERNAME
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

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

    user_email = notification_data.get("user_email")
    user_name = notification_data.get("user_name")
    admin_email = notification_data.get("admin_email")
    file_name = notification_data.get("file_name")
    existing_product_ids = notification_data.get("existing_product_ids", [])
    problematic_product_ids = notification_data.get("problematic_product_ids", [])
    product = notification_data.get("product", {})
    status = notification_data.get("status")

    if status == "notify_success":
        product_details = "\n".join([f"{key}: {value}" for key, value in product.items()])

        subject = "Product Upload Successful"

        message = f"Hi admin,\n\nUser {user_name} ({user_email}) uploaded a product within '{file_name}' with the following details:\n\n{product_details}"

        if existing_product_ids:
            message += f"\n\nUser also tried to upload products that already exist in the system. Here are the IDs:\n{', '.join(existing_product_ids)}"

        if problematic_product_ids:
            message += (
                f"\n\nSome products encountered errors during the upload. Please check the system logs for more details. Here are the IDs:\n{', '.join(problematic_product_ids)}"
            )

    else:
        subject = "Product Upload Failed"
        message = f"Hi admin,\n\nWhile user {user_name} ({user_email}) was uploading document '{file_name}', an error occurred."

    send_email(subject, admin_email, message)
