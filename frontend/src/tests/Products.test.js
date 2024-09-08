// src/tests/Products.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter as Router } from 'react-router-dom';
import Products from '../pages/Products';

describe('Products Component without data', () => {
    test('renders Products component correctly with no products', () => {
        render(
            <Router>
                <Products />
            </Router>
        );

        // There should be no products available
        expect(screen.getByText(/No products available/i)).toBeInTheDocument();
    });

    test('renders upload section correctly with no file uploaded', () => {
        render(
            <Router>
                <Products />
            </Router>
        );

        const fileInput = screen.getByRole('button', { name: /Upload/i });
        expect(fileInput).toBeInTheDocument();
    });

    test('handles filter form with no products loaded', () => {
        render(
            <Router>
                <Products />
            </Router>
        );

        // Filter form elements should be present
        expect(screen.getByLabelText(/Condition/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/Gender/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/Brand/i)).toBeInTheDocument();
    });

    test('renders pagination buttons when no products are available', () => {
        render(
            <Router>
                <Products />
            </Router>
        );

        // There should be no pagination buttons
        expect(screen.queryByText('1')).not.toBeInTheDocument();
    });

});
