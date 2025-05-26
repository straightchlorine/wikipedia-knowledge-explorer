import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter, useNavigate } from "react-router-dom";
import '@testing-library/jest-dom';
import Explore from "../pages/Explore";

jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),  // keep other exports intact
    useNavigate: jest.fn(),                      // mock useNavigate
}));

const { DataComponent, Article, PopUp } = jest.requireActual("../pages/Explore");

global.fetch = jest.fn(() =>
    Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ articles: ["Article 1", "Article 2"] }),
    })
);

describe("SearchBar", () => {
    test("renders input and updates query", () => {
        render(<Explore />);
        const input = screen.getByPlaceholderText(/search/i);
        fireEvent.change(input, { target: { value: "bitcoin" } });
        expect(input).toHaveValue("bitcoin");
    });

    test("submits form and renders DataComponent", async () => {
        render(<Explore />);
        const input = screen.getByPlaceholderText(/search/i);
        fireEvent.change(input, { target: { value: "crypto" } });
        fireEvent.keyDown(input, { key: "Enter", code: "Enter" });

        expect(screen.getByTestId('loading-dots')).toBeVisible();

        await waitFor(() => {
            expect(screen.getByTestId('loading-dots')).toBeVisible();
        });
    });
});

describe("DataComponent", () => {
    test("fetches and displays articles", async () => {
        const fakeData = {
            articles: ["Article 1", "Article 2"]
        };

        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => fakeData,
        });

        render(
            <MemoryRouter>
                <DataComponent query="crypto" settings={{ resultCount: 5 }} />
            </MemoryRouter>
        );

        expect(screen.getByTestId('loading-dots')).toBeVisible();

        await waitFor(() => {
            expect(screen.getByText(/found articles/i)).toBeInTheDocument();
        });

        expect(screen.getByText("Article 1")).toBeInTheDocument();
        expect(screen.getByText("Article 2")).toBeInTheDocument();
    });

    test("handles API error", async () => {
        (global.fetch).mockImplementationOnce(() =>
            Promise.resolve({ ok: false })
        );

        const empty = {};

        render(
            <MemoryRouter>
                <DataComponent query="error-case" settings={empty} />
            </MemoryRouter>
        );

        await waitFor(() => {
            expect(screen.getByText(/failed to fetch data/i)).toBeInTheDocument();
        });
    });
});

describe("Article", () => {
    test("renders article title and summary button", () => {
        const openMock = jest.fn();
        render(<Article index={0} title="Test Title" open={openMock} />);

        expect(screen.getByText("Test Title")).toBeInTheDocument();
        const button = screen.getByText(/summary/i);
        fireEvent.click(button);
        expect(openMock).toHaveBeenCalled();
    });
});

describe("PopUp", () => {
    test("renders popup and handles close", () => {
        const closeMock = jest.fn();
        render(<PopUp closePopup={closeMock} />);
        expect(screen.getByText(/this is a popup/i)).toBeInTheDocument();
        const closeBtn = screen.getByText("X");
        fireEvent.click(closeBtn);
        expect(closeMock).toHaveBeenCalled();
    });

    test("clicking outside content closes popup", () => {
        const closeMock = jest.fn();
        const { container } = render(<PopUp closePopup={closeMock} />);
        fireEvent.click(container.querySelector(".popup-overlay"));
        expect(closeMock).toHaveBeenCalled();
    });
});

describe("Explore", () => {
    test("renders SearchBar container", () => {
        const { container } = render(<Explore />);
        expect(container.querySelector(".search-container")).toBeInTheDocument();
    });
});
