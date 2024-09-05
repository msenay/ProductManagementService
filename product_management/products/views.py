import logging

from django.contrib.auth import authenticate
from django.core.paginator import Paginator
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from products.core import handle_uploaded_file, notify_admins_for_products, notify_failure_to_admins
from products.models import CustomUser, Product
from products.serializers import UserSerializer, ProductSerializer

logger = logging.getLogger('products')


# AUTHENTICATION

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
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
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Signed up successfully!"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# views.py
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
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
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})

    if not CustomUser.objects.filter(username=username).exists():
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    return Response({"error": "Invalid Password."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
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
    return Response({"message": f"User {request.user.username} with an email {request.user.email} logged out successfully"}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    """
    Protected view endpoint.

    This endpoint is accessible only to authenticated users. It returns a
    message containing the authenticated user's username and email.

    Returns:
        Response: JSON response with a success message and status code 200 if
        the user is authenticated.
    """
    return Response({"message": f"User {request.user.username} with an email {request.user.email} is authenticated."})


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint.

    This endpoint can be used to check if the server is running properly. It is
    accessible without authentication and always returns a status of "ok".

    Returns:
        Response: JSON response with status "ok" and status code 200.
    """
    return Response({"status": "ok"}, status=status.HTTP_200_OK)


# PRODUCT MANAGEMENT

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def upload_products(request):
    """
    Upload products via an XML file.

    This endpoint allows authenticated users to upload an XML file containing product data.
    The XML file is parsed, and each product is saved to the database if it doesn't already exist.
    """

    file = request.FILES.get('file')
    if not file:
        return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

    all_admins = CustomUser.objects.filter(is_superuser=True, is_staff=True)

    try:
        existing_product_ids, problematic_product_ids, products = handle_uploaded_file(file)
        notify_admins_for_products(request.user, file.name, products, existing_product_ids, problematic_product_ids, all_admins)
    except Exception as e:
        logger.error(f"Error uploading file {file.name}", exc_info=e)
        notify_failure_to_admins(request.user, file.name, str(e), all_admins)
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Products uploaded successfully"}, status=status.HTTP_201_CREATED)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_products(request):
    """
    List products with pagination, filtering, and sorting.

    This endpoint returns a paginated list of products filtered by condition, gender, and brand.
    The list can be sorted by price and title in ascending and descending order.

    Returns:
        Response: JSON response containing the product data.
    """
    products = Product.objects.all()

    # Filtering
    condition = request.GET.get('condition')
    if condition:
        products = products.filter(condition=condition)

    gender = request.GET.get('gender')
    if gender:
        products = products.filter(gender=gender)

    brand = request.GET.get('brand')
    if brand:
        products = products.filter(brand=brand)

    # Sorting
    sort_by = request.GET.get('sort_by', 'title')
    order = request.GET.get('order', 'asc')
    if order == 'desc':
        sort_by = f'-{sort_by}'
    products = products.order_by(sort_by)

    # Pagination
    paginator = Paginator(products, 5)  # 5 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    serializer = ProductSerializer(page_obj, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_detail(request, product_id):
    """
    Retrieve details of a single product by ID.

    This endpoint returns detailed information about a specific product.

    Returns:
        Response: JSON response containing the product data.
    """
    try:
        product = Product.objects.get(id=product_id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        logger.error(f"Product with ID {product_id} not found.")
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error retrieving product with ID {product_id}: {e}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
