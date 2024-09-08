# type: ignore
from django.contrib.auth.models import AbstractUser
from django.db import models

import uuid


class CustomUser(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"


class Product(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("unisex", "Unisex"),
    ]

    id = models.CharField(primary_key=True, max_length=50, unique=True)
    title = models.CharField(max_length=255)
    product_type = models.CharField(max_length=255)
    link = models.URLField(max_length=500)
    description = models.TextField()
    image_link = models.URLField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percent = models.CharField(max_length=50, null=True, blank=True)
    availability = models.CharField(max_length=50)
    google_product_category = models.CharField(max_length=100, null=True, blank=True)
    brand = models.CharField(max_length=100)
    gtin = models.CharField(max_length=100)
    item_group_id = models.CharField(max_length=50)
    condition = models.CharField(max_length=50)
    age_group = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES)
    gender_orig_value = models.CharField(max_length=50, null=True, blank=True)
    quantity = models.IntegerField()
    adult = models.BooleanField(default=False)
    adwords_labels = models.CharField(max_length=255, null=True, blank=True)
    additional_images_count = models.IntegerField(null=True, blank=True)
    ios_url = models.URLField(max_length=500, null=True, blank=True)
    ios_app_store_id = models.CharField(max_length=100, null=True, blank=True)
    ios_app_name = models.CharField(max_length=100, null=True, blank=True)
    iphone_app_name = models.CharField(max_length=100, null=True, blank=True)
    iphone_app_store_id = models.CharField(max_length=100, null=True, blank=True)
    iphone_url = models.URLField(max_length=500, null=True, blank=True)
    android_package = models.CharField(max_length=100, null=True, blank=True)
    android_app_name = models.CharField(max_length=100, null=True, blank=True)
    options_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    icon_media_url = models.URLField(max_length=500, null=True, blank=True)
    all_sizes_skus = models.CharField(max_length=255, null=True, blank=True)
    sizes_of_all_skus = models.CharField(max_length=255, null=True, blank=True)
    product_season = models.CharField(max_length=100, null=True, blank=True)
    product_class = models.CharField(max_length=100, null=True, blank=True)
    custom_label_0 = models.CharField(max_length=255, null=True, blank=True)
    custom_label_1 = models.CharField(max_length=255, null=True, blank=True)
    custom_label_2 = models.CharField(max_length=255, null=True, blank=True)
    custom_label_3 = models.CharField(max_length=255, null=True, blank=True)
    custom_label_4 = models.CharField(max_length=255, null=True, blank=True)


    objects = models.Manager()

    def __str__(self):
        return self.title

    def to_dict(self):
        """
        Converts the Product instance to a dictionary.
        """
        return {
            "id": self.id,
            "title": self.title,
            "product_type": self.product_type,
            "link": self.link,
            "description": self.description,
            "image_link": self.image_link,
            "price": str(self.price),
            "sale_price": str(self.sale_price) if self.sale_price else None,
            "old_price": str(self.old_price) if self.old_price else None,
            "final_price": str(self.final_price),
            "discount_percent": str(self.discount_percent) if self.discount_percent else None,
            "availability": self.availability,
            "google_product_category": self.google_product_category,
            "brand": self.brand,
            "gtin": self.gtin,
            "item_group_id": self.item_group_id,
            "condition": self.condition,
            "age_group": self.age_group,
            "color": self.color,
            "gender": self.gender,
            "quantity": self.quantity,
            "adult": self.adult,
            "adwords_labels": self.adwords_labels,
            "additional_images_count": self.additional_images_count,
            "ios_url": self.ios_url,
            "ios_app_store_id": self.ios_app_store_id,
            "ios_app_name": self.ios_app_name,
            "android_package": self.android_package,
            "android_app_name": self.android_app_name,
            "options_percentage": str(self.options_percentage) if self.options_percentage else None,
            "icon_media_url": self.icon_media_url,
            "all_sizes_skus": self.all_sizes_skus,
            "sizes_of_all_skus": self.sizes_of_all_skus,
            "product_season": self.product_season,
            "product_class": self.product_class,
            "custom_label_0": self.custom_label_0,
            "custom_label_1": self.custom_label_1,
            "custom_label_2": self.custom_label_2,
            "custom_label_3": self.custom_label_3,
            "custom_label_4": self.custom_label_4,
        }
