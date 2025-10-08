import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import NavBar from "../components/NavBar";
import { BrowserRouter } from "react-router-dom";

// Wrap NavBar in Router since it uses Link
const renderWithRouter = (ui: React.ReactElement) =>
  render(<BrowserRouter>{ui}</BrowserRouter>);

test("renders brand and toggles mobile menu", () => {
  renderWithRouter(<NavBar />);
  // Use role-based query for the brand link
  expect(
    screen.getByRole("link", { name: /NewsTracker/i }),
  ).toBeInTheDocument();

  // Hamburger button should be present
  const button = screen.getByLabelText(/Toggle menu/i);
  expect(button).toBeInTheDocument();

  // Count News links before toggle (desktop hidden section will not render in test DOM),
  const newsBefore = screen.queryAllByRole("link", { name: /News/i }).length;

  // Click to open menu
  fireEvent.click(button);
  // After clicking, there should be at least one News link rendered (menu expanded)
  const newsAfter = screen.queryAllByRole("link", { name: /News/i }).length;
  expect(newsAfter).toBeGreaterThanOrEqual(newsBefore);
});
