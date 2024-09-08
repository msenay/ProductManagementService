# type: ignore
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
import xml.etree.ElementTree as ET

from unittest.mock import patch
import logging

from products.models import Product, CustomUser
from products.utils import get_text, get_float_text, get_attribute


class AuthenticatedTestCase(TestCase):
    """
    A base test class that sets up an authenticated user for tests.
    """

    def setUp(self):
        # Disable logging during tests
        logging.disable(logging.CRITICAL)
        self.client = APIClient()

        # Create and authenticate a test user
        self.user = CustomUser.objects.create_user(username="testuser", email="testuser@example.com", password="password123")
        token, created = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def tearDown(self):
        """
        Activate logging after each test.
        """
        logging.disable(logging.NOTSET)


class UserTests(TestCase):
    def setUp(self):
        """
        Set up the test environment before each test.

        This includes initializing the APIClient, defining the URLs for signup,
        login, logout, protected, and health check endpoints, and creating
        a valid user data dictionary for use in the tests.
        """
        # Disable logging during tests
        logging.disable(logging.CRITICAL)

        # Initialize the API client for making requests in the tests
        self.client = APIClient()

        # Define URLs for the signup, login, logout, protected view, and health check
        self.signup_url = reverse("signup")
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")
        self.protected_url = reverse("protected")
        self.health_check_url = reverse("health_check")

        # Define valid user data to use in the tests
        self.valid_user_data = {"username": "msenay", "email": "murat.senay@example.com", "password": "strongpassword123", "first_name": "Murat", "last_name": "Şenay"}

    def tearDown(self):
        """
        Activate logging after each test.
        """
        logging.disable(logging.NOTSET)

    def test_signup_with_valid_data(self):
        """
        Test user signup with valid data.

        This test verifies that a user can successfully sign up with valid
        credentials and receives a success message with a 201 status code.
        """
        # Send a POST request to the signup endpoint with valid user data
        response = self.client.post(self.signup_url, self.valid_user_data, format="json")

        # Check that the response status is 201 (Created)
        self.assertEqual(response.status_code, 201)

        # Check that the response contains the success message
        self.assertEqual(response.data["message"], "Signed up successfully!")

    def test_signup_with_short_password(self):
        """
        Test user signup with a short password.

        This test checks that attempting to sign up with a password less
        than 8 characters results in a 400 status code and the appropriate
        error message.
        """
        # Modify the valid user data to have a short password
        short_password_data = self.valid_user_data.copy()
        short_password_data["password"] = "123"

        # Send a POST request with the modified data
        response = self.client.post(self.signup_url, short_password_data, format="json")

        # Check that the response status is 409 (Conflict)
        self.assertEqual(response.status_code, 409)

        # Ensure the response contains the error about the short password
        self.assertIn("password", response.data)
        self.assertEqual(response.data["password"][0], "Password should have a minimum of 4 characters.")

    def test_signup_with_missing_username(self):
        """
        Test user signup with a missing username.

        This test ensures that trying to sign up without a username results
        in a 400 status code and the appropriate error message.
        """
        # Remove the username from the user data
        missing_username_data = self.valid_user_data.copy()
        del missing_username_data["username"]

        # Send a POST request with the modified data
        response = self.client.post(self.signup_url, missing_username_data, format="json")

        # Check that the response status is 409 (Conflict)
        self.assertEqual(response.status_code, 409)

        # Ensure the response contains the error about the missing username
        self.assertIn("username", response.data)

    def test_signup_with_duplicate_email(self):
        """
        Test user signup with a duplicate email.

        This test verifies that attempting to sign up with an email that is
        already in use results in a 409 status code and the appropriate
        error message.
        """
        # First, sign up with the valid user data to create the user
        self.client.post(self.signup_url, self.valid_user_data, format="json")

        # Create a new user data dictionary with the same email
        duplicate_email_data = self.valid_user_data.copy()
        duplicate_email_data["username"] = "anotheruser"  # Change the username to avoid conflict

        # Send a POST request with the duplicate email
        response = self.client.post(self.signup_url, duplicate_email_data, format="json")

        # Check that the response status is 409 (Conflict)
        self.assertEqual(response.status_code, 409)

        # Ensure the response contains the error about the duplicate email
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"][0], "user with this email already exists.")

    def test_signup_with_duplicate_username(self):
        """
        Test user signup with a duplicate username.

        This test verifies that attempting to sign up with a username that is
        already in use results in a 409 status code and the appropriate
        error message.
        """
        # First, sign up with the valid user data to create the user
        self.client.post(self.signup_url, self.valid_user_data, format="json")

        # Create a new user data dictionary with the same username but different email
        duplicate_username_data = self.valid_user_data.copy()
        duplicate_username_data["email"] = "another.email@example.com"  # Change the email to avoid conflict

        # Send a POST request with the duplicate username
        response = self.client.post(self.signup_url, duplicate_username_data, format="json")

        # Check that the response status is 409 (Conflict)
        self.assertEqual(response.status_code, 409)

        # Ensure the response contains the error about the duplicate username
        self.assertIn("username", response.data)
        self.assertEqual(response.data["username"][0], "A user with that username already exists.")

    def test_login_with_valid_credentials(self):
        """
        Test user login with valid credentials.

        This test verifies that a user can successfully log in with valid
        credentials and receives an authentication token with a 200 status code.
        """
        # First, sign up the user
        self.client.post(self.signup_url, self.valid_user_data, format="json")

        # Define login data with the correct credentials
        login_data = {"username": "msenay", "password": "strongpassword123"}

        # Send a POST request to the login endpoint
        response = self.client.post(self.login_url, login_data, format="json")

        # Check that the response status is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Ensure the response contains the authentication token
        self.assertIn("token", response.data)

    def test_login_with_invalid_password(self):
        """
        Test user login with an invalid password.

        This test checks that attempting to log in with a wrong password
        results in a 400 status code and the appropriate error message.
        """
        # First, sign up the user
        self.client.post(self.signup_url, self.valid_user_data, format="json")

        # Define login data with the wrong password
        login_data = {"username": "msenay", "password": "wrongpassword"}

        # Send a POST request with invalid credentials
        response = self.client.post(self.login_url, login_data, format="json")

        # Check that the response status is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)

        # Ensure the response contains the error message for invalid password
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Invalid Password.")

    def test_login_with_nonexistent_user(self):
        """
        Test user login with a nonexistent username.

        This test ensures that trying to log in with a username that does not
        exist in the database results in a 404 status code and the appropriate
        error message.
        """
        # Define login data with a nonexistent username
        login_data = {"username": "nonexistent", "password": "somepassword"}

        # Send a POST request with the nonexistent username
        response = self.client.post(self.login_url, login_data, format="json")

        # Check that the response status is 404 (Not Found)
        self.assertEqual(response.status_code, 404)

        # Ensure the response contains the error message for user not found
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "User not found.")

    def test_protected_view_without_authentication(self):
        """
        Test accessing protected view without authentication.

        This test verifies that trying to access the protected view without
        being authenticated results in a 401 Unauthorized status code.
        """
        # Send a GET request to the protected endpoint without authentication
        response = self.client.get(self.protected_url)

        # Check that the response status is 401 (Unauthorized)
        self.assertEqual(response.status_code, 401)

    def test_protected_view_with_authentication(self):
        """
        Test accessing protected view with authentication.

        This test ensures that an authenticated user can successfully access
        the protected view and receives a 200 status code.
        """
        # First, sign up the user and log in to get a token
        self.client.post(self.signup_url, self.valid_user_data, format="json")
        login_data = {"username": "msenay", "password": "strongpassword123"}
        response = self.client.post(self.login_url, login_data, format="json")

        # Set the token in the headers
        token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        # Send a GET request to the protected endpoint with the token
        response = self.client.get(self.protected_url)

        # Check that the response status is 200 (OK)
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        """
        Test user logout.

        This test verifies that an authenticated user can log out successfully,
        and receives a success message with a 200 status code.
        """
        # Sign up and log in to get the token
        self.client.post(self.signup_url, self.valid_user_data, format="json")
        login_data = {"username": "msenay", "password": "strongpassword123"}
        response = self.client.post(self.login_url, login_data, format="json")

        # Set the token in the headers for authentication
        token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        # Send a POST request to the logout endpoint
        response = self.client.post(self.logout_url)

        # Check that the response status is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Ensure the response contains the logout success message
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], f"User {self.valid_user_data['username']} with an email {self.valid_user_data['email']} logged out successfully")

    def test_health_check(self):
        """
        Test health check endpoint.

        This test ensures that the health check endpoint returns a status of "ok"
        with a 200 status code, confirming the server is running properly.
        """
        # Send a GET request to the health check endpoint
        response = self.client.get(self.health_check_url)

        # Check that the response status is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Ensure the response contains the status "ok"
        self.assertEqual(response.data["status"], "ok")


class ProductUploadTests(AuthenticatedTestCase):
    def setUp(self):
        """
        Set up the test environment before each test.

        This includes initializing the APIClient, defining the URLs for product upload,
        and creating a test user who is authenticated for the tests.
        """
        # Call the parent class's setUp method to initialize the authenticated user
        super().setUp()
        # Reverse resolves the 'upload_products' URL name to its actual URL
        self.upload_url = reverse("upload_products")

    @patch("products.views.notify_admins_for_products")
    def test_upload_valid_products(self, mock_notify_admins_for_products):
        """
        Test uploading a valid product XML file.

        This test ensures that a valid XML file can be uploaded and products are created successfully.
        """
        # XML data that represents a valid product
        xml_data = b"""<?xml version="1.0" encoding="UTF-8"?>
            <rss xmlns:g="http://base.google.com/ns/1.0">
                <channel>
                    <item>
                        <g:id>67890</g:id>
                        <title>New Test Product</title>
                        <g:product_type>Electronics</g:product_type>
                        <link>https://example.com/product/67890</link>
                        <description>This is a new test product.</description>
                        <g:image_link>https://example.com/images/67890.jpg</g:image_link>
                        <g:price>199.99</g:price>
                        <g:sale_price>179.99</g:sale_price>
                        <g:finalprice>179.99</g:finalprice>
                        <g:availability>preorder</g:availability>
                        <g:google_product_category>Electronics</g:google_product_category>
                        <g:brand>NewBrand</g:brand>
                        <g:gtin>6789012345678</g:gtin>
                        <g:item_group_id>678</g:item_group_id>
                        <g:condition>new</g:condition>
                        <g:age_group>adult</g:age_group>
                        <g:color>black</g:color>
                        <g:gender>unisex</g:gender>
                        <g:quantity>5</g:quantity>
                        <g:custom_label_0>Label A</g:custom_label_0>
                        <g:custom_label_1>Label B</g:custom_label_1>
                        <g:custom_label_2>Label C</g:custom_label_2>
                        <g:custom_label_3>Label D</g:custom_label_3>
                        <g:custom_label_4>Label E</g:custom_label_4>
                    </item>
                </channel>
            </rss>"""

        # Create a file object with the XML data
        file = SimpleUploadedFile("feed.xml", xml_data, content_type="application/xml")

        # Send a POST request to upload the file
        response = self.client.post(self.upload_url, {"file": file}, format="multipart")

        # Assert that the response status code is 201 (Created)
        self.assertEqual(response.status_code, 201)

        # Ensure that one product is created in the database
        self.assertEqual(Product.objects.count(), 1)

        # Fetch the created product by its ID
        created_product = Product.objects.get(id="67890")
        self.assertIsNotNone(created_product)

        # Verify that each product field is correctly populated
        self.assertEqual(created_product.title, "New Test Product")
        self.assertEqual(float(created_product.price), 199.99)
        self.assertEqual(float(created_product.sale_price), 179.99)
        self.assertEqual(created_product.google_product_category, "Electronics")
        self.assertEqual(created_product.gtin, "6789012345678")
        self.assertEqual(created_product.gender, "unisex")
        self.assertEqual(created_product.custom_label_0, "Label A")

        # Ensure that notify_admins_for_products was called
        mock_notify_admins_for_products.assert_called()

    def test_upload_with_no_file(self):
        """
        Test uploading without providing a file.

        This test checks that if no file is provided, a 400 status code is returned with an error message.
        """
        # Send a POST request without a file
        response = self.client.post(self.upload_url, {}, format="multipart")

        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)

        # Ensure that the response contains the error message
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "No file provided")

    @patch("products.views.notify_failure_to_admins")
    def test_upload_invalid_xml_file(self, mock_notify_failure_to_admins):
        """
        Test uploading an invalid XML file.

        This test ensures that when an invalid XML file is uploaded, the error is handled properly and
        failure notification is sent to admins.
        """
        # Invalid XML data that cannot be parsed
        invalid_xml_data = b"Invalid XML Content"

        # Create a file object with invalid XML data
        file = SimpleUploadedFile("invalid_feed.xml", invalid_xml_data, content_type="application/xml")

        # Send a POST request to upload the invalid file
        response = self.client.post(self.upload_url, {"file": file}, format="multipart")

        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)

        # Ensure the error message is related to XML parsing
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "syntax error: line 1, column 0")

        # Ensure that notify_failure_to_admins was called
        mock_notify_failure_to_admins.assert_called()


class ProductListTests(AuthenticatedTestCase):
    def setUp(self):
        """
        Set up the test environment before each test.

        This includes initializing the APIClient, creating a user, obtaining
        an authentication token, and creating sample product data.
        """
        # Call the parent class's setUp method to initialize the authenticated user
        super().setUp()

        self.list_products_url = reverse("list_products")

        # Create sample products with all necessary fields
        Product.objects.bulk_create(
            [
                Product(
                    id="1",
                    title="Product A",
                    product_type="Type1",
                    link="http://example.com/a",
                    description="Description A",
                    image_link="http://example.com/a.jpg",
                    price=10.0,
                    final_price=10.0,
                    availability="in stock",
                    google_product_category="Category1",
                    brand="BrandX",
                    gtin="111111",
                    item_group_id="001",
                    condition="new",
                    age_group="adult",
                    color="red",
                    gender="unisex",
                    quantity=100,
                ),
                Product(
                    id="2",
                    title="Product B",
                    product_type="Type2",
                    link="http://example.com/b",
                    description="Description B",
                    image_link="http://example.com/b.jpg",
                    price=20.0,
                    final_price=18.0,
                    availability="preorder",
                    google_product_category="Category2",
                    brand="BrandY",
                    gtin="222222",
                    item_group_id="002",
                    condition="used",
                    age_group="adult",
                    color="blue",
                    gender="male",
                    quantity=50,
                ),
                Product(
                    id="3",
                    title="Product C",
                    product_type="Type1",
                    link="http://example.com/c",
                    description="Description C",
                    image_link="http://example.com/c.jpg",
                    price=30.0,
                    final_price=28.0,
                    availability="out of stock",
                    google_product_category="Category3",
                    brand="BrandX",
                    gtin="333333",
                    item_group_id="003",
                    condition="new",
                    age_group="adult",
                    color="green",
                    gender="female",
                    quantity=25,
                ),
                Product(
                    id="4",
                    title="Product D",
                    product_type="Type2",
                    link="http://example.com/d",
                    description="Description D",
                    image_link="http://example.com/d.jpg",
                    price=40.0,
                    final_price=38.0,
                    availability="in stock",
                    google_product_category="Category1",
                    brand="BrandY",
                    gtin="444444",
                    item_group_id="004",
                    condition="new",
                    age_group="teen",
                    color="black",
                    gender="unisex",
                    quantity=10,
                ),
                Product(
                    id="5",
                    title="Product E",
                    product_type="Type1",
                    link="http://example.com/e",
                    description="Description E",
                    image_link="http://example.com/e.jpg",
                    price=50.0,
                    final_price=45.0,
                    availability="preorder",
                    google_product_category="Category2",
                    brand="BrandZ",
                    gtin="555555",
                    item_group_id="005",
                    condition="used",
                    age_group="teen",
                    color="yellow",
                    gender="female",
                    quantity=5,
                ),
                Product(
                    id="6",
                    title="Product F",
                    product_type="Type2",
                    link="http://example.com/f",
                    description="Description F",
                    image_link="http://example.com/f.jpg",
                    price=60.0,
                    final_price=55.0,
                    availability="in stock",
                    google_product_category="Category3",
                    brand="BrandX",
                    gtin="666666",
                    item_group_id="006",
                    condition="new",
                    age_group="adult",
                    color="purple",
                    gender="male",
                    quantity=200,
                ),
            ]
        )

    def test_list_products_pagination(self):
        """
        Test product list pagination.

        This test ensures that the product list is paginated correctly with 5 products per page.
        """
        response = self.client.get(self.list_products_url, {"page": 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 5)  # Check that 5 products are returned on the first page

        # Test second page
        response = self.client.get(self.list_products_url, {"page": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)  # Only one product should be on the second page

    def test_list_products_filtering(self):
        """
        Test product list filtering.

        This test ensures that products can be filtered by condition, gender, and brand.
        """
        # Filter by condition "new"
        response = self.client.get(self.list_products_url, {"condition": "new"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 4)

        # Filter by gender "female"
        response = self.client.get(self.list_products_url, {"gender": "female"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 2)

        # Filter by brand "BrandX"
        response = self.client.get(self.list_products_url, {"brand": "BrandX"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 3)

    def test_list_products_sorting(self):
        """
        Test product list sorting.

        This test ensures that products can be sorted by price and title in ascending and descending order.
        """
        # Sort by price ascending
        response = self.client.get(self.list_products_url, {"sort_by": "price", "order": "asc"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["title"], "Product A")  # Lowest price should be first

        # Sort by price descending
        response = self.client.get(self.list_products_url, {"sort_by": "price", "order": "desc"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["title"], "Product F")  # Highest price should be first

        # Sort by title ascending
        response = self.client.get(self.list_products_url, {"sort_by": "title", "order": "asc"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["title"], "Product A")  # Alphabetically first

        # Sort by title descending
        response = self.client.get(self.list_products_url, {"sort_by": "title", "order": "desc"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["title"], "Product F")  # Alphabetically last


class ProductDetailTests(AuthenticatedTestCase):
    def setUp(self):
        """
        Set up the test environment before each test.

        This includes initializing the APIClient, creating a user, obtaining
        an authentication token, and creating sample product data.
        """
        # Call the parent class's setUp method to initialize the authenticated user
        super().setUp()
        self.product_detail_url = reverse("product_detail", kwargs={"product_id": "1"})

        # Create a sample product
        self.product = Product.objects.create(
            id="1",
            title="Product A",
            product_type="Type1",
            link="http://example.com/a",
            description="Description A",
            image_link="http://example.com/a.jpg",
            price=10.0,
            final_price=10.0,
            availability="in stock",
            google_product_category="Category1",
            brand="BrandX",
            gtin="111111",
            item_group_id="001",
            condition="new",
            age_group="adult",
            color="red",
            gender="unisex",
            quantity=100,
        )

    def test_product_detail_success(self):
        """
        Test retrieving product details successfully.

        This test verifies that a product can be retrieved successfully with
        the correct product ID, and a 200 status code is returned.
        """
        response = self.client.get(self.product_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.product.id)
        self.assertEqual(response.data["title"], self.product.title)
        self.assertEqual(response.data["price"], f"{self.product.price:.2f}")

    def test_product_detail_not_found(self):
        """
        Test retrieving a product that does not exist.

        This test ensures that attempting to retrieve a non-existing product
        returns a 404 status code with an appropriate error message.
        """
        non_existent_product_url = reverse("product_detail", kwargs={"product_id": "9999"})
        response = self.client.get(non_existent_product_url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["error"], "Product not found.")

    def test_product_detail_error(self):
        """
        Test handling an unexpected error during product retrieval.

        This test verifies that if an unexpected error occurs, a 400 status
        code is returned and an error message is logged.
        """
        with patch("products.views.Product.objects.get") as mock_get:
            mock_get.side_effect = Exception("Unexpected Error")
            response = self.client.get(self.product_detail_url)

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Unexpected Error")


class ProductFilterTests(AuthenticatedTestCase):
    def setUp(self):
        """
        Call parent setUp method to initialize authentication and
        then set up test data specific to this test case.
        """
        super().setUp()

        # Create sample products with all necessary fields
        Product.objects.create(
            id="1",
            title="Product A",
            product_type="Type1",
            link="http://example.com/a",
            description="Description A",
            image_link="http://example.com/a.jpg",
            price=10.0,
            final_price=10.0,
            availability="in stock",
            google_product_category="Category1",
            brand="BrandX",
            gtin="111111",
            item_group_id="001",
            condition="new",
            age_group="adult",
            color="red",
            gender="unisex",
            quantity=100,
        )
        Product.objects.create(
            id="2",
            title="Product B",
            product_type="Type2",
            link="http://example.com/b",
            description="Description B",
            image_link="http://example.com/b.jpg",
            price=20.0,
            final_price=18.0,
            availability="preorder",
            google_product_category="Category2",
            brand="BrandY",
            gtin="222222",
            item_group_id="002",
            condition="used",
            age_group="adult",
            color="blue",
            gender="male",
            quantity=50,
        )
        Product.objects.create(
            id="3",
            title="Product C",
            product_type="Type3",
            link="http://example.com/c",
            description="Description C",
            image_link="http://example.com/c.jpg",
            price=30.0,
            final_price=28.0,
            availability="out of stock",
            google_product_category="Category3",
            brand="BrandZ",
            gtin="333333",
            item_group_id="003",
            condition="new",
            age_group="adult",
            color="green",
            gender="female",
            quantity=25,
        )

    def test_filter_options(self):
        """
        Test to ensure that the product filters return distinct values for condition, gender, and brand.
        """
        url = reverse("filter_options")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Extract the returned filter values
        conditions = response.data["conditions"]
        genders = response.data["genders"]
        brands = response.data["brands"]

        # Assert that the correct distinct values are returned
        self.assertCountEqual(conditions, ["new", "used"])
        self.assertCountEqual(genders, ["unisex", "male", "female"])
        self.assertCountEqual(brands, ["BrandX", "BrandY", "BrandZ"])


class TestUtils(TestCase):
    """
    Unit tests for utility functions defined in the 'products.utils' module.

    This test class includes unit tests for the following utility functions:
    - get_text: Safely retrieves text from an XML element, returning a default value if the element or its text is None.
    - get_float_text: Safely retrieves a floating-point number from an XML element's text, returning a default value if the element or text is None or raises a ValueError for
    invalid floats.

    Each test method validates different cases, including:
    - Valid XML elements with text.
    - XML elements without text, expecting default values.
    - Handling of None elements.
    - Handling of valid and invalid float values in XML text.

    These tests ensure that the utility functions behave correctly and robustly handle edge cases.
    """

    def test_get_text_element_with_text(self):
        element = ET.Element("test")
        element.text = "sample text"
        self.assertEqual(get_text(element, "default text"), "sample text")

    def test_get_text_element_without_text(self):
        element = ET.Element("test")
        self.assertEqual(get_text(element, "default text"), "default text")

    def test_get_text_element_none(self):
        self.assertEqual(get_text(None, "default text"), "default text")

    def test_get_float_text_element_with_valid_float(self):
        element = ET.Element("test")
        element.text = "123.45"
        self.assertEqual(get_float_text(element, 0.0), 123.45)

    def test_get_float_text_element_with_valid_float_and_extra_spaces(self):
        element = ET.Element("test")
        element.text = "123.45 extra"
        self.assertEqual(get_float_text(element, 0.0), 123.45)

    def test_get_float_text_element_with_invalid_float(self):
        element = ET.Element("test")
        element.text = "invalid"
        with self.assertRaises(ValueError):
            get_float_text(element, 0.0)

    def test_get_float_text_element_none(self):
        self.assertEqual(get_float_text(None, 0.0), 0.0)

    def test_get_float_text_element_with_default(self):
        self.assertEqual(get_float_text(None, 99.99), 99.99)

    def test_get_attribute_with_value(self):
        element = ET.Element("test")
        element.set("content", "attribute value")
        self.assertEqual(get_attribute(element, "content"), "attribute value")

    def test_get_attribute_with_default(self):
        element = ET.Element("test")
        self.assertEqual(get_attribute(element, "non_existent_attribute", "default value"), "default value")

    def test_get_attribute_none_element(self):
        self.assertEqual(get_attribute(None, "content", "default value"), "default value")

    def test_get_attribute_with_no_attribute(self):
        element = ET.Element("test")
        self.assertEqual(get_attribute(element, "non_existent_attribute", "default value"), "default value")
