import { render, screen } from "@testing-library/react";
import { RouterProvider } from "react-router-dom";
import { router } from "../routes/routes";

const OLD_ENV = process.env;

beforeEach(() => {
  jest.resetModules(); // clear module cache so imports re-evaluate with new env
  process.env = { ...OLD_ENV, VITE_API_ENDPOINT: "http://localhost:1234" };
});

afterAll(() => {
  process.env = OLD_ENV; // restore env
});

// smoke test to ensure app renders routes
test("renders landing page content via App", () => {
  render(<RouterProvider router={router} />);
  // Landing should contain at least one 'Latest News' heading
  const headings = screen.getAllByRole("heading", { name: /Latest News/i });
  expect(headings.length).toBeGreaterThanOrEqual(1);
});
