import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Explore from './Explore';

global.fetch = vi.fn();

beforeEach(() => {
    fetch.mockReset();
});

describe('Explore', () => {
    test('renders search input', () => {
        render(
            <MemoryRouter>
                <Explore />
            </MemoryRouter>
        );
        expect(screen.getByPlaceholderText(/search wikipedia/i)).toBeInTheDocument();
    });

    test('renders result count slider with default value 5', () => {
        render(
            <MemoryRouter>
                <Explore />
            </MemoryRouter>
        );
        const slider = screen.getByRole('slider');
        expect(slider).toBeInTheDocument();
        expect(slider.value).toBe('5');
    });

    test('updates query as user types', () => {
        render(
            <MemoryRouter>
                <Explore />
            </MemoryRouter>
        );
        const input = screen.getByPlaceholderText(/search wikipedia/i);
        fireEvent.change(input, { target: { value: 'quantum' } });
        expect(input.value).toBe('quantum');
    });

    test('does not fetch when search query is empty', () => {
        render(
            <MemoryRouter>
                <Explore />
            </MemoryRouter>
        );
        const button = screen.getByRole('button', { name: /search/i });
        fireEvent.click(button);
        expect(fetch).not.toHaveBeenCalled();
    });

    test('fetches articles and shows results after form submission', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({
                articles: [
                    { title: 'Quantum mechanics', summary: 'A summary.' },
                    { title: 'Wave function', summary: null },
                ],
            }),
        });

        render(
            <MemoryRouter>
                <Explore />
            </MemoryRouter>
        );

        const input = screen.getByPlaceholderText(/search wikipedia/i);
        fireEvent.change(input, { target: { value: 'quantum' } });
        fireEvent.submit(input.closest('form'));

        await waitFor(() => {
            expect(screen.getByText('Quantum mechanics')).toBeInTheDocument();
        });
        expect(screen.getByText('Wave function')).toBeInTheDocument();
    });

    test('shows error message when fetch fails', async () => {
        fetch.mockResolvedValueOnce({ ok: false });

        render(
            <MemoryRouter>
                <Explore />
            </MemoryRouter>
        );

        const input = screen.getByPlaceholderText(/search wikipedia/i);
        fireEvent.change(input, { target: { value: 'error' } });
        fireEvent.submit(input.closest('form'));

        await waitFor(() => {
            expect(screen.getByText(/Failed to fetch data/i)).toBeInTheDocument();
        });
    });

    test('shows Found Articles heading after successful fetch', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ articles: ['Article 1', 'Article 2'] }),
        });

        render(
            <MemoryRouter>
                <Explore />
            </MemoryRouter>
        );

        const input = screen.getByPlaceholderText(/search wikipedia/i);
        fireEvent.change(input, { target: { value: 'test' } });
        fireEvent.submit(input.closest('form'));

        await waitFor(() => {
            expect(screen.getByText(/Found Articles/i)).toBeInTheDocument();
        });
    });
});
