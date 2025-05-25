jest.mock('d3', () => { });
import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';

describe('App routing', () => {
    test('renders Home component on default route "/"', () => {
        render(
            <MemoryRouter initialEntries={['/']}>
                <App />
            </MemoryRouter>
        );
        expect(screen.getByRole('heading', { name: /Wikipedia Knowledge Explorer/i })).toBeInTheDocument();
    });

    test('renders Explore component on "/explore"', () => {
        const { container } = render(
            <MemoryRouter initialEntries={['/explore']}>
                <App />
            </MemoryRouter>
        );
        expect(container.querySelector('.search-container')).toBeInTheDocument();
    });

    test('renders About component on "/about"', () => {
        render(
            <MemoryRouter initialEntries={['/about']}>
                <App />
            </MemoryRouter>
        );
        expect(screen.getByRole('heading', { name: /About the Project/i })).toBeInTheDocument();
    });

    test('renders Visualize component on "/visualize"', () => {
        render(
            <MemoryRouter initialEntries={['/visualize']}>
                <App />
            </MemoryRouter>
        );
        expect(screen.getByRole('heading', { name: /Visualization of phrase:.*/i })).toBeInTheDocument();
    });

    test('renders NoPage component on invalid route', () => {
        render(
            <MemoryRouter initialEntries={['/unknown']}>
                <App />
            </MemoryRouter>
        );
        expect(screen.getByText(/not found|404|no page/i)).toBeInTheDocument();
    });
});
