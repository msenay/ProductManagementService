import xml.etree.ElementTree as ET
import logging
from typing import List, Tuple, Dict, Optional
from django.db.models import QuerySet

from products.enums import DocumentEventsEnum
from products.models import Product, CustomUser
from products.tasks.product import send_notification
from products.serializers import ProductSerializer

logger = logging.getLogger(__name__)


def handle_uploaded_file(file) -> Tuple[List[str], List[str], List[Dict]]:
    """
    Processes the uploaded XML file and returns product data.

    Args:
        file: The uploaded XML file.

    Returns:
        Tuple containing:
            - existing_product_ids (List[str]): IDs of products that already exist in the database.
            - problematic_product_ids (List[str]): IDs of products that failed to be created.
            - products (List[Dict]): List of successfully created products, serialized.
    """
    logger.info(f"Processing file {file.name}...")
    try:
        tree = ET.parse(file)
        root = tree.getroot()
    except Exception as e:
        logger.error(f"Failed to parse XML file {file.name}", exc_info=e)
        raise e

    namespace = {"g": "http://base.google.com/ns/1.0"}
    existing_product_ids: List[str] = []
    problematic_product_ids: List[str] = []
    product_instances_list: List[Dict] = []

    for item in root.findall("./channel/item"):
        product_id: str = item.find("g:id", namespace).text

        if Product.objects.filter(id=product_id).exists():
            existing_product_ids.append(product_id)
            continue

        try:
            product_instance = create_product_instance(item, namespace)
            serialized_product = ProductSerializer(product_instance).data
            product_instances_list.append(serialized_product)
            logger.info(f"Product with ID {product_id} successfully created.")
        except Exception as e:
            logger.error(f"Failed to create product with {product_id=}", exc_info=e)
            problematic_product_ids.append(product_id)

    return existing_product_ids, problematic_product_ids, product_instances_list


def create_product_instance(item: ET.Element, namespace: Dict[str, str]) -> Product:
    """
    Helper function to create a Product instance from an XML item.

    Args:
        item (ET.Element): The XML element representing the product.
        namespace (Dict[str, str]): The XML namespace.

    Returns:
        Product: The created Product instance.
    """
    product_id: str = item.find("g:id", namespace).text
    title: str = item.find("title").text
    product_type: str = item.find("g:product_type", namespace).text
    link: str = item.find("link").text
    description: str = item.find("description").text
    image_link: str = item.find("g:image_link", namespace).text
    price: float = float(item.find("g:price", namespace).text.split()[0])
    sale_price_text: Optional[str] = item.find("g:sale_price", namespace).text
    sale_price: Optional[float] = float(sale_price_text.split()[0]) if sale_price_text else None
    finalprice: float = float(item.find("g:finalprice", namespace).text.split()[0])
    availability: str = item.find("g:availability", namespace).text
    google_product_category: str = item.find("g:google_product_category", namespace).text
    brand: str = item.find("g:brand", namespace).text
    gtin: str = item.find("g:gtin", namespace).text
    item_group_id: str = item.find("g:item_group_id", namespace).text
    condition: str = item.find("g:condition", namespace).text
    age_group: str = item.find("g:age_group", namespace).text
    color: str = item.find("g:color", namespace).text
    gender: str = item.find("g:gender", namespace).text
    quantity: int = int(item.find("g:quantity", namespace).text)

    custom_labels: List[str] = [item.find(f"g:custom_label_{i}", namespace).text or "" for i in range(5)]

    product_instance: Product = Product.objects.create(
        id=product_id,
        title=title,
        product_type=product_type,
        link=link,
        description=description,
        image_link=image_link,
        price=price,
        sale_price=sale_price,
        finalprice=finalprice,
        availability=availability,
        google_product_category=google_product_category,
        brand=brand,
        gtin=gtin,
        item_group_id=item_group_id,
        condition=condition,
        age_group=age_group,
        color=color,
        gender=gender,
        quantity=quantity,
        custom_label_0=custom_labels[0],
        custom_label_1=custom_labels[1],
        custom_label_2=custom_labels[2],
        custom_label_3=custom_labels[3],
        custom_label_4=custom_labels[4],
    )

    return product_instance


def notify_admins_for_products(
    user: CustomUser, file_name: str, products: List[Dict], existing_product_ids: List[str], problematic_product_ids: List[str], all_admins: QuerySet
) -> None:
    """
    Notify admins for each successfully uploaded product.

    Args:
        user (CustomUser): The user who uploaded the products.
        file_name (str): The name of the uploaded file.
        products (List[Dict]): List of serialized product data that were successfully created.
        existing_product_ids (List[str]): List of product IDs that already existed in the database.
        problematic_product_ids (List[str]): List of product IDs that could not be processed.
        all_admins (QuerySet): List of admin users who will be notified.

    Returns:
        None: Sends notifications and logs the notification status.
    """
    for admin in all_admins:
        for product in products:
            notification_data = {
                "user_email": user.email,
                "user_name": user.username,
                "admin_email": admin.email,
                "file_name": file_name,
                "existing_product_ids": existing_product_ids,
                "problematic_product_ids": problematic_product_ids,
                "product": product,
                "status": DocumentEventsEnum.NOTIFY_SUCCESS.value,
            }
            logger.info(f"Sending notification to {admin.email} for product {product['id']}")
            send_notification.send(notification_data)


def notify_failure_to_admins(user: CustomUser, file_name: str, error: str, all_admins: QuerySet) -> None:
    """
    Notify admins if the product upload failed.

    Args:
        user (CustomUser): The user who attempted the upload.
        file_name (str): The name of the file that caused the error.
        error (str): The error message that was generated during the upload.
        all_admins (QuerySet): List of admin users who will be notified.

    Returns:
        None: Sends failure notifications and logs the failure.
    """
    for admin in all_admins:
        try:
            notification_data = {
                "user_email": user.email,
                "user_name": user.username,
                "admin_email": admin.email,
                "file_name": file_name,
                "status": DocumentEventsEnum.NOTIFY_FAILURE.value,
                "error": error,
            }
            logger.info(f"Sending failure notification to {admin.email} for file {file_name}")
            send_notification.send(notification_data)
        except Exception as e:
            logger.error(f"Failed to notify admin {admin.email} of file {file_name} error: {e}", exc_info=True)
