import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import '@testing-library/jest-dom';
import Visualize from "../components/Visualize";

const { GraphComponent, GetLinks } = jest.requireActual("../components/Visualize");

jest.mock("d3", () => {
  const originalD3 = jest.requireActual("d3");
  return {
    ...originalD3,
    select: () => ({
      selectAll: () => ({
        remove: jest.fn(),
        data: () => ({
          join: () => ({
            attr: jest.fn(),
            text: jest.fn(),
            call: jest.fn(),
            append: jest.fn(),
          }),
        }),
      }),
      append: () => ({
        attr: jest.fn(),
        selectAll: () => ({
          data: () => ({
            join: () => ({
              attr: jest.fn(),
              text: jest.fn(),
              call: jest.fn(),
              append: jest.fn(),
            }),
          }),
        }),
      }),
      attr: jest.fn(),
    }),
    forceSimulation: () => ({
      force: jest.fn().mockReturnThis(),
      on: jest.fn(),
      restart: jest.fn(),
      alphaTarget: jest.fn().mockReturnThis(),
    }),
    forceLink: () => ({
      id: jest.fn().mockReturnThis(),
      distance: jest.fn().mockReturnThis(),
    }),
    forceManyBody: () => ({
      strength: jest.fn().mockReturnThis(),
    }),
    forceCenter: () => ({}),
    drag: () => ({
      on: jest.fn().mockReturnThis(),
    }),
    scaleOrdinal: () => () => "blue",
    schemeCategory10: ["blue", "green", "red"],
  };
});

global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({
      articles: [
        { title: "A1", cluster: 0 },
        { title: "A2", cluster: 0 },
        { title: "B1", cluster: 1 },
        { title: "B2", cluster: 1 },
      ]
    })
  })
);

describe("GetLinks", () => {
  test("returns expected links between clusters", () => {
    const data = {
      articles: [
        { title: "T1", cluster: 0 },
        { title: "T2", cluster: 0 },
        { title: "T3", cluster: 1 },
        { title: "T4", cluster: 1 },
      ],
    };
    const links = GetLinks(data);
    expect(links).toEqual([
      { source: "T1", target: "T3" },
      { source: "T1", target: "T4" },
      { source: "T2", target: "T3" },
      { source: "T2", target: "T4" }
    ]);
  });
});

describe("GraphComponent", () => {
  test("renders Graph after fetching data", async () => {
    render(
      <GraphComponent query="test" />
    );
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
  });

  test("shows error message if fetch fails", async () => {
    (global.fetch as jest.Mock).mockImplementationOnce(() =>
      Promise.resolve({ ok: false })
    );
    render(<GraphComponent query="fail" />);
    await waitFor(() => {
      expect(screen.getByText(/failed to fetch data/i)).toBeInTheDocument();
    });
  });
});

describe("Visualize", () => {
  test("renders title and GraphComponent", async () => {
    render(
      <MemoryRouter initialEntries={["/visualize?query=test"]}>
        <Routes>
          <Route path="/visualize" element={<Visualize />} />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByText(/visualization of phrase: test/i)).toBeInTheDocument();
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
  });
});
