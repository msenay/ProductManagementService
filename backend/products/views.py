import logging
from typing import List, Optional

from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.authtoken.models import Token

from products.enums import ProductPagination
from products.core import handle_uploaded_file, notify_admins_for_products, notify_failure_to_admins
from products.models import CustomUser, Product
from products.serializers import UserSerializer, ProductSerializer, ProductFilterSerializer

logger = logging.getLogger("products")


# AUTHENTICATION


@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request) -> Response:
    """
    User signup endpoint.

    This endpoint allows a new user to sign up by providing their username,
    email, password, first name, and last name. Upon successful registration,
    a success message is returned. If the provided data is invalid, an error
    message is returned.

    Returns:
        Response: JSON response with a success message and status code 201 if
        registration is successful, or an error message and status code 400 if
        there are validation errors.
    """
    serializer = UserSerializer(data=request.data)
    try:
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            logger.info(f"New user signed up: {serializer.data.get('username')}")
            return Response({"message": "Signed up successfully!"}, status=status.HTTP_201_CREATED)
    except serializers.ValidationError as e:
        logger.warning("Signup failed.", exc_info=e)
        return Response(e.detail, status=status.HTTP_409_CONFLICT)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request) -> Response:
    """
    User login endpoint.

    This endpoint authenticates a user using their username and password.
    Upon successful authentication, an authentication token is returned.
    If the username or password is incorrect, an appropriate error message
    is returned.

    Returns:
        Response: JSON response with the authentication token and status code 200
        if login is successful, or an error message with appropriate status codes
        if authentication fails.
    """
    username: Optional[str] = request.data.get("username")
    password: Optional[str] = request.data.get("password")

    user: Optional[CustomUser] = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        logger.info(f"User {username} logged in.")
        return Response({"token": token.key, "username": username}, status=status.HTTP_200_OK)

    if not CustomUser.objects.filter(username=username).exists():
        logger.error(f"Login failed: User {username} not found.")
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    logger.warning(f"Login failed: Invalid password for user {username}.")
    return Response({"error": "Invalid Password."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request) -> Response:
    """
    User logout endpoint.

    This endpoint allows an authenticated user to log out. The user's
    authentication token is deleted, effectively logging them out of the system.
    A success message with the user's username and email is returned.

    Returns:
        Response: JSON response with a success message and status code 200 if
        logout is successful.
    """
    request.user.auth_token.delete()
    logger.info(f"User {request.user.username} logged out successfully.")
    return Response({"message": f"User {request.user.username} with an email {request.user.email} logged out successfully"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def protected_view(request) -> Response:
    """
    Protected view endpoint.

    This endpoint is accessible only to authenticated users. It returns a
    message containing the authenticated user's username and email.

    Returns:
        Response: JSON response with a success message and status code 200 if
        the user is authenticated.
    """
    logger.info(f"Protected view accessed by {request.user.username}.")
    return Response({"message": f"User {request.user.username} with an email {request.user.email} is authenticated."}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request) -> Response:
    """
    Health check endpoint.

    This endpoint can be used to check if the server is running properly. It is
    accessible without authentication and always returns a status of "ok".

    Returns:
        Response: JSON response with status "ok" and status code 200.
    """
    return Response({"status": "ok"}, status=status.HTTP_200_OK)


# PRODUCT MANAGEMENT


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def upload_products(request) -> Response:
    """
    Upload products via an XML file.

    This endpoint allows authenticated users to upload an XML file containing product data.
    The XML file is parsed, and each product is saved to the database if it doesn't already exist.
    """

    file = request.FILES.get("file")
    if not file:
        logger.error("No file provided for upload.")
        return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

    all_admins = CustomUser.objects.filter(is_superuser=True, is_staff=True)

    try:
        existing_product_ids, problematic_product_ids, products = handle_uploaded_file(file)
        notify_admins_for_products(request.user, file.name, products, existing_product_ids, problematic_product_ids, all_admins)
        logger.info(f"Products uploaded successfully by {request.user.username}: {file.name}")
    except Exception as e:
        logger.error(f"Error uploading file {file.name}", exc_info=e)
        notify_failure_to_admins(request.user, file.name, str(e), all_admins)
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Products uploaded successfully"}, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_products(request) -> Response:
    """
    List products with pagination, filtering, and sorting.
    """
    # Validate and parse query parameters
    serializer = ProductFilterSerializer(data=request.GET)
    serializer.is_valid(raise_exception=True)
    filters = serializer.validated_data

    products = Product.objects.all()

    # Filtering
    condition = filters.get("condition")
    if condition:
        products = products.filter(condition=condition)

    gender = filters.get("gender")
    if gender:
        products = products.filter(gender=gender)

    brand = filters.get("brand")
    if brand:
        products = products.filter(brand=brand)

    # Sorting
    sort_by = filters.get("sort_by", "title")
    order = filters.get("order", "asc")
    if order == "desc":
        sort_by = f"-{sort_by}"
    products = products.order_by(sort_by)

    # Pagination
    paginator = ProductPagination()
    paginated_products = paginator.paginate_queryset(products, request)
    serializer = ProductSerializer(paginated_products, many=True)

    # Adding total pages to the response
    response_data = paginator.get_paginated_response(serializer.data).data
    response_data["total_pages"] = paginator.page.paginator.num_pages

    logger.info(f"Products listed for user {request.user.username}. Filters applied: {filters}")
    return Response(response_data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def product_detail(request, product_id: str) -> Response:
    """
    Retrieve details of a single product by ID.

    This endpoint returns detailed information about a specific product.

    Returns:
        Response: JSON response containing the product data.
    """
    try:
        product = Product.objects.get(id=product_id)
        serializer = ProductSerializer(product)
        logger.info(f"Product {product_id} details retrieved for user {request.user.username}.")
        return Response(serializer.data)
    except Product.DoesNotExist:
        logger.error(f"Product with ID {product_id} not found.", exc_info=True)
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error retrieving product with ID {product_id}: {e}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def filter_options(request) -> Response:
    """
    Get distinct filter values for condition, gender, and brand.
    Returns distinct values for the condition, gender, and brand fields.
    """
    conditions: List[str] = Product.objects.values_list("condition", flat=True).distinct()
    genders: List[str] = Product.objects.values_list("gender", flat=True).distinct()
    brands: List[str] = Product.objects.values_list("brand", flat=True).distinct()

    logger.info(f"Filter options retrieved for user {request.user.username}.")
    return Response({"conditions": list(conditions), "genders": list(genders), "brands": list(brands)})
