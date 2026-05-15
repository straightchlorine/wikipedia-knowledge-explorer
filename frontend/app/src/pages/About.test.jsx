import { render, screen } from '@testing-library/react';
import About from './About';

describe('About', () => {
    test('renders main heading', () => {
        render(<About />);
        expect(screen.getByRole('heading', { name: /About the Project/i })).toBeInTheDocument();
    });

    test('renders project description', () => {
        render(<About />);
        expect(screen.getByText(/Wikipedia Knowledge Explorer/i)).toBeInTheDocument();
        expect(screen.getByText(/intelligent clustering, summarization, and visualization/i)).toBeInTheDocument();
    });

    test('renders tech stack section', () => {
        render(<About />);
        expect(screen.getByRole('heading', { name: /Tech Stack/i })).toBeInTheDocument();
        expect(screen.getByText('React')).toBeInTheDocument();
        expect(screen.getByText('FastAPI')).toBeInTheDocument();
        expect(screen.getByText('D3.js')).toBeInTheDocument();
    });

    test('renders GitHub link', () => {
        render(<About />);
        const link = screen.getByRole('link', { name: /View on GitHub/i });
        expect(link).toBeInTheDocument();
        expect(link).toHaveAttribute('href', expect.stringContaining('github.com'));
    });
});
