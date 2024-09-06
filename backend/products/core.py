import xml.etree.ElementTree as ET
import logging

from products.enums import DocumentEventsEnum
from products.models import Product
from products.tasks.product import send_notification

logger = logging.getLogger(__name__)


def handle_uploaded_file(file):
    logger.info(f"Processing file {file.name}...")
    try:
        tree = ET.parse(file)
        root = tree.getroot()
    except Exception as e:
        logger.error(f"Failed to parse XML file {file.name}", exc_info=e)
        raise e

    namespace = {'g': 'http://base.google.com/ns/1.0'}
    existing_product_ids = []
    problematic_product_ids = []
    product_instances_list = []

    for item in root.findall('./channel/item'):
        product_id = item.find('g:id', namespace).text

        if Product.objects.filter(id=product_id).exists():
            existing_product_ids.append(product_id)
            continue

        try:
            product_instance = create_product_instance(item, namespace)
            product_instances_list.append(product_instance.to_dict())
            logger.info(f"Product with ID {product_id} successfully created.")
        except Exception as e:
            logger.error(f"Failed to create product with {product_id=}", exc_info=e)
            problematic_product_ids.append(product_id)

    return existing_product_ids, problematic_product_ids, product_instances_list


def create_product_instance(item, namespace):
    """
    Helper function to create a Product instance from an XML item.
    """
    product_id = item.find('g:id', namespace).text
    title = item.find('title').text
    product_type = item.find('g:product_type', namespace).text
    link = item.find('link').text
    description = item.find('description').text
    image_link = item.find('g:image_link', namespace).text
    price = float(item.find('g:price', namespace).text.split()[0])
    sale_price_text = item.find('g:sale_price', namespace).text or None
    sale_price = float(sale_price_text.split()[0]) if sale_price_text else None
    finalprice = float(item.find('g:finalprice', namespace).text.split()[0])
    availability = item.find('g:availability', namespace).text
    google_product_category = item.find('g:google_product_category', namespace).text
    brand = item.find('g:brand', namespace).text
    gtin = item.find('g:gtin', namespace).text
    item_group_id = item.find('g:item_group_id', namespace).text
    condition = item.find('g:condition', namespace).text
    age_group = item.find('g:age_group', namespace).text
    color = item.find('g:color', namespace).text
    gender = item.find('g:gender', namespace).text
    quantity = int(item.find('g:quantity', namespace).text)
    custom_labels = [item.find(f'g:custom_label_{i}', namespace).text or '' for i in range(5)]

    product_instance = Product.objects.create(
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


def notify_admins_for_products(user, file_name, products, existing_product_ids, problematic_product_ids, all_admins):
    """
    Notify admins for each uploaded product.
    """
    for admin in all_admins:
        for product in products:
            notification_data = {
                'user_email': user.email,
                'user_name': user.username,
                'admin_email': admin.email,
                'file_name': file_name,
                'existing_product_ids': existing_product_ids,
                'problematic_product_ids': problematic_product_ids,
                'product': product,
                'status': DocumentEventsEnum.NOTIFY_SUCCESS.value,
            }
            logger.info(f"Sending notification to {admin.email} for product {product['id']}")
            send_notification.send(notification_data)


def notify_failure_to_admins(user, file_name, error, all_admins):
    """
    Notify admins if the product upload failed.
    """
    for admin in all_admins:
        notification_data = {
            'user_email': user.email,
            'user_name': user.username,
            'admin_email': admin.email,
            'file_name': file_name,
            'status': DocumentEventsEnum.NOTIFY_FAILURE.value,
            'error': error,
        }
        send_notification.send(notification_data)
