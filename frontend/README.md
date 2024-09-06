# Ounass Product Management Frontend

This project is the frontend part of the Ounass Product Management platform. The platform allows users to upload, filter, and view product listings with detailed information. The frontend is built using React.js and interacts with the backend APIs to manage products and user authentication.

## Key Technologies Used

<p><b>React.js:</b>A JavaScript library for building user interfaces.</p>
<p><b>Axios:</b> For making HTTP requests to the backend API.</p>
<p><b>React Router:</b> For navigation between different pages (Login, Register, Product List).</p>
<p><b>CSS:</b> Basic styling to structure and present the components.</p>
<p><b>Environment Variables:</b> To handle API URL and other sensitive data.</p>

## Features

### Authentication
<p><b>Register:</b> Users can create a new account by providing a username, email, password, first name, and last name.</p>
<p><b>Login:</b> Existing users can log in by providing their username and password.</p>
<p><b>Logout:</b> Authenticated users can log out using the button in the top-right corner.</p>

### Product Management
<p><b>Upload Products:</b> Users can upload product data through a file input.</p>
<p><b>Filter Products:</b> Users can filter the products based on condition, gender, brand, and sort the list by title or price.</p>
<p><b>View Product List:</b> The table displays product details such as title, description, price, and other product-specific information. Pagination is implemented to navigate through multiple pages of products.</p>

## Folder Structure

```text
src/
│
├── components/                 # Reusable components used across pages
│   ├── Layout.js               # Main layout component with header, footer, and content area
│   └── PrivateRoute.js         # Ensures certain routes are accessible only to authenticated users
│
├── pages/                      # Specific pages for the application
│   ├── Products.js             # Page to view, filter, and upload products
│   ├── SignIn.js               # User sign-in (login) page
│   └── SignUp.js               # User sign-up (registration) page
│
├── services/                   # Service layer or API-related configuration
│   └── setupAxios.js           # Axios configuration, including interceptors for token handling
│
├── styles/                     # CSS styles for the application
│   ├── App.css                 # Main stylesheet for the App component
│   └── index.css               # Global styles for the application
│
├── tests/                      # Test files for various components and functionality
│   ├── App.test.js             # Tests for the main App component
│   ├── SignIn.test.js          # Unit tests for the SignIn component
│   └── SignUp.test.js          # Unit tests for the SignUp component
│
├── App.js                      # Main component that renders the entire application
├── index.js                    # Entry point to the React application, renders the App component
├── reportWebVitals.js          # For measuring and reporting app performance
└── setupTests.js               # Configuration and setup for Jest testing

```
## How to Run the Project

### Clone the repository:
```bash
git clone https://github.com/msenay/ProductManagementService.git
cd frontend
```

### Install dependencies: Make sure you have Node.js and npm installed on your machine.
```bash
npm install
```
### ENV Variables
Set up environment variables: Create a .env file in the root directory with using .env.template as a template.

### Start the development server:
```bash
npm start
```
### Access the application: 
Open http://localhost:3000 in your browser to see the application in action.

### API Endpoints

The frontend interacts with the following backend API endpoints:
```text
/login/: Authenticates users.
/signup/: Registers new users.
/list-products/: Fetches the list of products.
/upload-products/: Allows users to upload product data.
/filter-options/: Provides filter options like conditions, gender, and brands.
```
### Authentication

The application uses JWT tokens for authentication. After logging in, the token is stored in localStorage, and it is sent with each API request that requires authorization.

### Testing
```bash
npm test -- --watchAll=false
```