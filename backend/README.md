# Ounass Product Management Backend

This is the backend service for the Ounass Product Management platform. It handles user authentication, product management, file uploads, and background tasks such as sending email notifications. The backend is built using Django, Django Rest Framework (DRF), and Dramatiq for task queueing. It uses a PostgreSQL database to store all user and product data.

## Key Technologies Used

Django: The main framework used for handling HTTP requests and responses.
Django Rest Framework (DRF): Provides RESTful API functionalities.
PostgreSQL: The database used to store user and product information.
Dramatiq: A task queue system to handle background tasks like sending emails.
JWT Authentication: Token-based authentication for secure access.
Logging: The system logs key events for better traceability of errors and actions.
Features

## Authentication
<p>Signup: Users can create an account with username, email, password, first name, and last name.</p>
<p>Login: Users can log in to receive a token, which is needed for accessing protected routes.</p>
<p>Logout: Authenticated users can log out by invalidating their token.</p>
<p>Protected Routes: Some routes require a valid JWT token to access.</p>

## Product Management
<p>Upload Products: Authenticated users can upload product data via an XML file. Products are stored in the database after validation.</p>
<p>List Products: Paginated product listings with filtering and sorting options.</p>
<p>Product Detail: Retrieve detailed information about a specific product by ID.</p>
<p>Filter Options: Retrieve filter options like condition, gender, and brand for use in the product list.</p>

## Background Tasks
#### Dramatiq Tasks: 

<p>Dramatiq is used for sending email notifications to admins after a product upload. </p>
<p>It sends each product to admins email. It also handles failures by notifying admins about errors during the process.For test purposes we are generating an admin user automatically. </p>
<p>Only you have do is set it on env before run.</p>


## Folder Structure

```text
backend/
│
├── product_management/         # Main project directory
│   ├── __init__.py             # Project initialization
│   ├── asgi.py                 # ASGI configuration
│   ├── settings.py             # Main settings file (env variables loaded here)
│   ├── urls.py                 # Global URL routing
│   └── wsgi.py                 # WSGI configuration
│
├── products/                   # App directory for product management
│   ├── migrations/             # Database migrations
│   ├── tasks/                  # Dramatiq tasks
│   │   ├── product.py          # Task for sending notification emails
│   │   └── tasks.py            # Helper tasks and retry mechanisms
│   ├── admin.py                # Admin interface configurations
│   ├── apps.py                 # App configurations
│   ├── core.py                 # Core functionalities such as file handling
│   ├── enums.py                # Enums for constants and event types
│   ├── models.py               # Database models for CustomUser and Product
│   ├── serializers.py          # Serializers for API inputs/outputs
│   ├── tests.py                # Unit tests for API functionality
│   ├── urls.py                 # URL routing specific to product management
│   └── views.py                # API views for handling requests
│
├── .env                        # Environment variables (excluded from version control)
├── .env.template               # Template for creating .env file
├── .gitignore                  # Ignored files for Git
├── Dockerfile                  # Docker configuration for deployment
├── manage.py                   # Django command-line utility
├── Ounass_Case_Study.postman_collection.json # Postman API collection for testing
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
└── run_api                     # Shell script to run the API
```

## Setting Up the Project

#### Clone the repository:
```bash
git clone https://github.com/msenay/ProductManagementService.git
cd backend
```
Install dependencies: Make sure you have Python 3.x and PostgreSQL installed. Then, install the required Python packages:
```bash
pip install -r requirements.txt
Set up environment variables: Copy the .env.template file to create your own .env file:
```
```bash
cp .env.template .env
```
Then, modify the .env file with your specific configuration, such as the database URL, email settings, and Dramatiq configuration.

#### Run database migrations: 
Apply the migrations to set up the database schema:
```bash
python manage.py migrate
```
Run the development server: Start the development server to test the APIs:
```bash
python manage.py runserver
```
### API Endpoints

Authentication Endpoints
```text
/signup/ (POST): Register a new user.
/login/ (POST): Log in an existing user and retrieve the authentication token.
/logout/ (POST): Log out an authenticated user by invalidating their token.
/auth-protected-check/ (GET): Verify that the user is authenticated.
/health-check/ (GET): Check if the server is running.
Product Management Endpoints
/upload-products/ (POST): Upload products via an XML file.
/list-products/ (GET): List all products with pagination, filtering, and sorting.
/product-detail/<product_id>/ (GET): Retrieve detailed information about a specific product.
/filter-options/ (GET): Retrieve distinct filter options for condition, gender, and brand.
```
### Email System & Dramatiq Task

The backend uses Dramatiq to handle background tasks such as sending email notifications after a product upload. When an authenticated user uploads a file, the following happens:

The XML file is processed, and products are either added to the database or flagged as existing/problematic.
An email is sent to all admins containing information about the uploaded products, using the send_notification task from the tasks directory.
Task Workflow
The Dramatiq task send_notification sends an email to each admin using the provided SMTP settings.
If the upload fails, the Dramatiq task notifies admins of the error.
You can configure the SMTP server, email address, and password in the .env file.

### Postman Collection

A postman.json file is included in the repository, which contains a set of API requests. You can import this collection into Postman for easier testing of the backend.
```text
Open Postman.
Go to File > Import.
Select the Ounass_Case_Study.postman_collection.json file from the project.
Use the imported requests to test the backend APIs.
```

### Testing
```bash
docker-compose run api python manage.py test
```