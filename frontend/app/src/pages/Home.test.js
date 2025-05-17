import React from "react";
import { render, screen } from "@testing-library/react";
import Home from "../components/Home";
import '@testing-library/jest-dom';

describe("Home", () => {
  test("renders main heading", () => {
    render(<Home />);
    expect(screen.getByRole("heading", { name: /wikipedia knowledge explorer/i })).toBeInTheDocument();
  });

  test("renders introductory paragraph", () => {
    render(<Home />);
    expect(screen.getByText(/interactive prototype that helps users explore/i)).toBeInTheDocument();
  });

  test("renders 'What it does' section with list items", () => {
    render(<Home />);
    expect(screen.getByRole("heading", { name: /what it does/i })).toBeInTheDocument();
    expect(screen.getByText(/users enter a search term/i)).toBeInTheDocument();
    expect(screen.getByText(/k-means clustering algorithm/i)).toBeInTheDocument();
    expect(screen.getByText(/automatically summarized/i)).toBeInTheDocument();
    expect(screen.getByText(/interactive graph showing topic clusters/i)).toBeInTheDocument();
  });

  test("renders 'Project Goal' section", () => {
    render(<Home />);
    expect(screen.getByRole("heading", { name: /project goal/i })).toBeInTheDocument();
    expect(screen.getByText(/make information discovery easier/i)).toBeInTheDocument();
  });
});
