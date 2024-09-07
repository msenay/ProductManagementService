from django.urls import path
from products.views import signup, login, protected_view, logout, health_check, upload_products, list_products, product_detail, filter_options

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path("auth-protected-check/", protected_view, name="protected"),
    path("health-check/", health_check, name="health_check"),
    path("upload-products/", upload_products, name="upload_products"),
    path("list-products/", list_products, name="list_products"),
    path("product-detail/<str:product_id>/", product_detail, name="product_detail"),
    path("filter-options/", filter_options, name="filter_options"),
]
