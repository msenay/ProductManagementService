import xml.etree.ElementTree as ET
from typing import Optional


def get_text(element: Optional[ET.Element], default: Optional[str]) -> Optional[str]:
    return element.text if element is not None and element.text is not None else default


def get_float_text(element: Optional[ET.Element], default: Optional[float]) -> Optional[float]:
    return float(element.text.split()[0]) if element is not None and element.text else default


def get_attribute(element: Optional[ET.Element], attribute: str, default: Optional[str] = None) -> Optional[str]:
    return element.attrib.get(attribute, default) if element is not None else default


def format_product_details(product: dict) -> str:
    """Formats product details as an HTML string with bold keys and line breaks."""
    formatted_details = "<br>".join([f"<strong>{key}:</strong> {value}" for key, value in product.items()])
    return f"<p>{formatted_details}</p>"


def create_email_html(
    subject: str, user_name: str, user_email: str, file_name: str, product_details: dict, existing_product_ids: list, problematic_product_ids: list, status: str
) -> str:
    """Create an HTML version of the email content with a simplified design, using header, body, and footer only."""

    formatted_product_details = format_product_details(product_details)

    existing_products_html = f"<p><strong>Existing Product IDs:</strong> {', '.join(existing_product_ids)}</p>" if existing_product_ids else ""
    problematic_products_html = f"<p><strong>Problematic Product IDs:</strong> {', '.join(problematic_product_ids)}</p>" if problematic_product_ids else ""

    if status == "notify_success":
        message_body = f"""
        <p>User <strong>{user_name}</strong> ({user_email}) uploaded a product within '{file_name}' with the following details:</p>
        {formatted_product_details}
        {existing_products_html}
        {problematic_products_html}
        """
    else:
        message_body = f"""
        <p>While user {user_name} ({user_email}) was uploading document '{file_name}', an error occurred.</p>
        """

    return f"""
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
                font-family: Arial, sans-serif;
            }}

            header {{
                padding: 20px;
                background-color: #000;
                color: #fff;
                text-align: center;
                font-size: 24px;
                font-weight: bold;
            }}

            .body {{
                padding: 20px;
                background-color: white;
                max-width: 800px;
                margin: 20px auto;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
            }}

            footer {{
                background-color: #000;
                color: #fff;
                text-align: center;
                padding: 10px;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <header>
            Ounass
        </header>

        <div class="body">
            <h1>{subject}</h1>
            {message_body}
        </div>

        <footer>
            <p>Thank you,<br>Ounass</p>
        </footer>
    </body>
    </html>
    """
