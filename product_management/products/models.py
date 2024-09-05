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
        ('male', 'Male'),
        ('female', 'Female'),
        ('unisex', 'Unisex'),
    ]

    id = models.CharField(primary_key=True, max_length=50, unique=True)
    title = models.CharField(max_length=255)
    product_type = models.CharField(max_length=255)
    link = models.URLField(max_length=500)
    description = models.TextField()
    image_link = models.URLField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    finalprice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    availability = models.CharField(max_length=50)
    google_product_category = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    gtin = models.CharField(max_length=100)
    item_group_id = models.CharField(max_length=50)
    condition = models.CharField(max_length=50)
    age_group = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    gender = models.CharField(max_length=50, choices=GENDER_CHOICES)
    quantity = models.IntegerField()
    custom_label_0 = models.CharField(max_length=255, null=True, blank=True)
    custom_label_1 = models.CharField(max_length=255, null=True, blank=True)
    custom_label_2 = models.CharField(max_length=255, null=True, blank=True)
    custom_label_3 = models.CharField(max_length=255, null=True, blank=True)
    custom_label_4 = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title

    def to_dict(self):
        """
        Converts the Product instance to a dictionary.
        """
        return {
            'id': self.id,
            'title': self.title,
            'product_type': self.product_type,
            'link': self.link,
            'description': self.description,
            'image_link': self.image_link,
            'price': str(self.price),
            'sale_price': str(self.sale_price) if self.sale_price else None,
            'finalprice': str(self.finalprice),
            'availability': self.availability,
            'google_product_category': self.google_product_category,
            'brand': self.brand,
            'gtin': self.gtin,
            'item_group_id': self.item_group_id,
            'condition': self.condition,
            'age_group': self.age_group,
            'color': self.color,
            'gender': self.gender,
            'quantity': self.quantity,
            'custom_label_0': self.custom_label_0,
            'custom_label_1': self.custom_label_1,
            'custom_label_2': self.custom_label_2,
            'custom_label_3': self.custom_label_3,
            'custom_label_4': self.custom_label_4,
        }
