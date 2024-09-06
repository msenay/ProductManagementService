import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter as Router } from 'react-router-dom';
import axios from 'axios';
import SignUp from '../pages/SignUp';


// Mock axios
jest.mock('axios');

describe('SignUp Component', () => {
    test('renders SignUp component correctly', () => {
        render(
            <Router>
                <SignUp />
            </Router>
        );

        // Check if the elements are rendered
        expect(screen.getByPlaceholderText(/Username/i)).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/Email/i)).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/Password/i)).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/First Name/i)).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/Last Name/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /Register/i })).toBeInTheDocument();
    });

    test('handles user input correctly', () => {
        render(
            <Router>
                <SignUp />
            </Router>
        );

        const usernameInput = screen.getByPlaceholderText(/Username/i);
        const emailInput = screen.getByPlaceholderText(/Email/i);
        const passwordInput = screen.getByPlaceholderText(/Password/i);
        const firstNameInput = screen.getByPlaceholderText(/First Name/i);
        const lastNameInput = screen.getByPlaceholderText(/Last Name/i);

        // Simulate typing in inputs
        fireEvent.change(usernameInput, { target: { value: 'testuser' } });
        fireEvent.change(emailInput, { target: { value: 'testuser@test.com' } });
        fireEvent.change(passwordInput, { target: { value: 'password123' } });
        fireEvent.change(firstNameInput, { target: { value: 'John' } });
        fireEvent.change(lastNameInput, { target: { value: 'Doe' } });

        expect(usernameInput.value).toBe('testuser');
        expect(emailInput.value).toBe('testuser@test.com');
        expect(passwordInput.value).toBe('password123');
        expect(firstNameInput.value).toBe('John');
        expect(lastNameInput.value).toBe('Doe');
    });

    test('displays error message on failed registration', async () => {
        // Mock a failed registration request
        axios.post.mockRejectedValue({
            response: { data: { username: ['This username is already taken.'] } },
        });

        render(
            <Router>
                <SignUp />
            </Router>
        );

        const usernameInput = screen.getByPlaceholderText(/Username/i);
        const emailInput = screen.getByPlaceholderText(/Email/i);
        const passwordInput = screen.getByPlaceholderText(/Password/i);
        const firstNameInput = screen.getByPlaceholderText(/First Name/i);
        const lastNameInput = screen.getByPlaceholderText(/Last Name/i);
        const registerButton = screen.getByRole('button', { name: /Register/i });

        fireEvent.change(usernameInput, { target: { value: 'testuser' } });
        fireEvent.change(emailInput, { target: { value: 'testuser@test.com' } });
        fireEvent.change(passwordInput, { target: { value: 'password123' } });
        fireEvent.change(firstNameInput, { target: { value: 'John' } });
        fireEvent.change(lastNameInput, { target: { value: 'Doe' } });

        // Simulate form submission
        fireEvent.click(registerButton);

        // Wait for the error message to appear
        const errorMessage = await screen.findByText(/This username is already taken./i);
        expect(errorMessage).toBeInTheDocument();
    });
});
