import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Home from './Home';

describe('Home', () => {
    test('renders main heading', () => {
        render(
            <MemoryRouter>
                <Home />
            </MemoryRouter>
        );
        expect(screen.getByRole('heading', { name: /Explore Wikipedia Knowledge Visually/i })).toBeInTheDocument();
    });

    test('renders introductory paragraph', () => {
        render(
            <MemoryRouter>
                <Home />
            </MemoryRouter>
        );
        expect(screen.getByText(/Search, cluster, and visualize Wikipedia articles/i)).toBeInTheDocument();
    });

    test('renders Start Exploring link', () => {
        render(
            <MemoryRouter>
                <Home />
            </MemoryRouter>
        );
        expect(screen.getByRole('link', { name: /Start Exploring/i })).toBeInTheDocument();
    });

    test('renders feature cards', () => {
        render(
            <MemoryRouter>
                <Home />
            </MemoryRouter>
        );
        expect(screen.getByText('Search')).toBeInTheDocument();
        expect(screen.getByText('Cluster')).toBeInTheDocument();
        expect(screen.getByText('Visualize')).toBeInTheDocument();
    });
});
