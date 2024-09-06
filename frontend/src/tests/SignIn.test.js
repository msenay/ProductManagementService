import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter as Router } from 'react-router-dom';
import axios from 'axios';
import SignIn from '../pages/SignIn';

// Mock axios
jest.mock('axios');

describe('SignIn Component', () => {
    test('renders SignIn component correctly', () => {
        render(
            <Router>
                <SignIn />
            </Router>
        );

        // Check if the elements are rendered
        expect(screen.getByPlaceholderText(/Username/i)).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/Password/i)).toBeInTheDocument();
        expect(screen.getByText(/Sign In/i)).toBeInTheDocument();
    });

    test('handles user input correctly', () => {
        render(
            <Router>
                <SignIn />
            </Router>
        );

        const usernameInput = screen.getByPlaceholderText(/Username/i);
        const passwordInput = screen.getByPlaceholderText(/Password/i);

        // Simulate typing in inputs
        fireEvent.change(usernameInput, { target: { value: 'testuser' } });
        fireEvent.change(passwordInput, { target: { value: 'password123' } });

        expect(usernameInput.value).toBe('testuser');
        expect(passwordInput.value).toBe('password123');
    });

    test('displays error message on failed login', async () => {
        // Mock a failed login request
        axios.post.mockRejectedValue({
            response: { data: { error: 'Login failed!' } },
        });

        render(
            <Router>
                <SignIn />
            </Router>
        );

        const usernameInput = screen.getByPlaceholderText(/Username/i);
        const passwordInput = screen.getByPlaceholderText(/Password/i);
        const loginButton = screen.getByText(/Login/i);

        fireEvent.change(usernameInput, { target: { value: 'testuser' } });
        fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });

        // Simulate form submission
        fireEvent.click(loginButton);

        // Wait for the error message to appear
        const errorMessage = await screen.findByText(/Login failed!/i);
        expect(errorMessage).toBeInTheDocument();
    });
});
