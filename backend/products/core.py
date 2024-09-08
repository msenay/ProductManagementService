import xml.etree.ElementTree as ET
import logging
from typing import List, Tuple, Dict, Optional
from django.db.models import QuerySet

from products.enums import DocumentEventsEnum
from products.models import Product, CustomUser
from products.tasks.product import send_notification
from products.serializers import ProductSerializer
from products.utils import get_text, get_float_text, get_attribute

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
        product_id: Optional[str] = get_text(item.find("g:id", namespace), None)

        if product_id and Product.objects.filter(id=product_id).exists():
            existing_product_ids.append(product_id)
            continue

        try:
            product_instance = create_product_instance(item, namespace)
            serialized_product = ProductSerializer(product_instance).data
            product_instances_list.append(serialized_product)
            logger.info(f"Product with ID {product_id} successfully created.")
        except Exception as e:
            logger.error(f"Failed to create product with {product_id=}", exc_info=e)
            if product_id:
                problematic_product_ids.append(product_id)
            else:
                logger.error("Product ID not found in XML item.")

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
    product_id: Optional[str] = get_text(item.find("g:id", namespace), None)
    title: Optional[str] = get_text(item.find("title"), None)
    product_type: Optional[str] = get_text(item.find("g:product_type", namespace), None)
    link: Optional[str] = get_text(item.find("link"), None)
    description: Optional[str] = get_text(item.find("description"), None)
    image_link: Optional[str] = get_text(item.find("g:image_link", namespace), None)
    price: Optional[float] = get_float_text(item.find("g:price", namespace), None)
    sale_price: Optional[float] = get_float_text(item.find("g:sale_price", namespace), None)
    old_price: Optional[float] = get_float_text(item.find("g:oldprice", namespace), None)
    final_price: Optional[float] = get_float_text(item.find("g:finalprice", namespace), None)
    discount_percent: Optional[str] = get_text(item.find("g:discount_percent", namespace), None)
    availability: Optional[str] = get_text(item.find("g:availability", namespace), None)
    google_product_category: Optional[str] = get_text(item.find("g:google_product_category", namespace), None)
    brand: Optional[str] = get_text(item.find("g:brand", namespace), None)
    gtin: Optional[str] = get_text(item.find("g:gtin", namespace), None)
    item_group_id: Optional[str] = get_text(item.find("g:item_group_id", namespace), None)
    condition: Optional[str] = get_text(item.find("g:condition", namespace), None)
    age_group: Optional[str] = get_text(item.find("g:age_group", namespace), None)
    color: Optional[str] = get_text(item.find("g:color", namespace), None)
    gender: Optional[str] = get_text(item.find("g:gender", namespace), None)
    quantity: int = int(get_text(item.find("g:quantity", namespace), "0") or "0")
    adult_str = get_text(item.find("g:adult", namespace), "no")
    adult: bool = adult_str.lower() == "yes" if adult_str else False
    adwords_labels: Optional[str] = get_text(item.find("g:adwords_labels", namespace), None)
    additional_images_count: Optional[int] = int(get_text(item.find("additional_images_count", namespace), "0") or "0")
    ios_url: Optional[Optional[str]] = get_text(item.find("g:ios_url", namespace), None)
    ios_app_store_id: Optional[Optional[str]] = get_text(item.find("g:ios_app_store_id", namespace), None)
    ios_app_name: Optional[Optional[str]] = get_text(item.find("g:ios_app_name", namespace), None)
    iphone_app_name: Optional[str] = get_attribute(item.find("appLink[@property='iphone_app_name']"), "content", None)
    iphone_app_store_id: Optional[str] = get_attribute(item.find("appLink[@property='iphone_app_store_id']"), "content", None)
    iphone_url: Optional[str] = get_attribute(item.find("appLink[@property='iphone_url']"), "content", None)

    android_package: Optional[Optional[str]] = get_text(item.find("g:android_package", namespace), None)
    android_app_name: Optional[Optional[str]] = get_text(item.find("g:android_app_name", namespace), None)
    options_percentage: Optional[float] = get_float_text(item.find("options_percentage", namespace), None)
    icon_media_url: Optional[Optional[str]] = get_text(item.find("icon_media_url", namespace), None)
    all_sizes_skus: Optional[Optional[str]] = get_text(item.find("all_sizes_skus", namespace), None)
    sizes_of_all_skus: Optional[Optional[str]] = get_text(item.find("sizes_of_all_skus", namespace), None)
    product_season: Optional[Optional[str]] = get_text(item.find("product_season", namespace), None)
    product_class: Optional[Optional[str]] = get_text(item.find("product_class", namespace), None)
    gender_orig_value: Optional[str] = get_text(item.find("g:gender_orig_value", namespace), None)

    custom_labels: List[Optional[str]] = [get_text(item.find(f"g:custom_label_{i}", namespace), None) for i in range(5)]

    product_instance: Product = Product.objects.create(
        id=product_id,
        title=title,
        product_type=product_type,
        link=link,
        description=description,
        image_link=image_link,
        price=price,
        sale_price=sale_price,
        old_price=old_price,
        final_price=final_price,
        discount_percent=discount_percent,
        availability=availability,
        google_product_category=google_product_category,
        brand=brand,
        gtin=gtin,
        item_group_id=item_group_id,
        condition=condition,
        age_group=age_group,
        color=color,
        gender=gender,
        gender_orig_value=gender_orig_value,
        quantity=quantity,
        adult=adult,
        adwords_labels=adwords_labels,
        additional_images_count=additional_images_count,
        ios_url=ios_url,
        ios_app_store_id=ios_app_store_id,
        ios_app_name=ios_app_name,
        android_package=android_package,
        android_app_name=android_app_name,
        options_percentage=options_percentage,
        icon_media_url=icon_media_url,
        all_sizes_skus=all_sizes_skus,
        sizes_of_all_skus=sizes_of_all_skus,
        product_season=product_season,
        product_class=product_class,
        custom_label_0=custom_labels[0],
        custom_label_1=custom_labels[1],
        custom_label_2=custom_labels[2],
        custom_label_3=custom_labels[3],
        custom_label_4=custom_labels[4],
        iphone_app_name=iphone_app_name,
        iphone_app_store_id=iphone_app_store_id,
        iphone_url=iphone_url,
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
