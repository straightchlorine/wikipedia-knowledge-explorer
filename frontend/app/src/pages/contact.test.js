import React from "react";
import { render, screen } from "@testing-library/react";
import About from "../components/About";
import '@testing-library/jest-dom';

describe("About", () => {
  test("renders heading and paragraphs", () => {
    render(<About />);
    expect(screen.getByRole("heading", { name: /about the project/i })).toBeInTheDocument();
    expect(screen.getByText(/wikipedia knowledge explorer/i)).toBeInTheDocument();
    expect(screen.getByText(/explore wikipedia content/i)).toBeInTheDocument();
  });
});
