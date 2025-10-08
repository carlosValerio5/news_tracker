import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

// Mock TitleBar and CustomGoogleLogin to isolate RegisterPage behavior
jest.mock("../components/TitleBar", () => () => (
  <div data-testid="mock-titlebar">TitleBar</div>
));
jest.mock("../components/CustomGoogleLogin", () => () => (
  <button data-testid="mock-google-login">Sign in with Google</button>
));

import RegisterPage from "../core/RegisterPage";

describe("RegisterPage", () => {
  test("renders heading, description, mocked TitleBar and Google login, and login link", () => {
    render(
      <MemoryRouter>
        <RegisterPage />
      </MemoryRouter>,
    );

    // Heading
    expect(
      screen.getByRole("heading", { name: /Register/i }),
    ).toBeInTheDocument();

    // Description text
    expect(
      screen.getByText(/Create your account with Google./i),
    ).toBeInTheDocument();

    // Mocked TitleBar should be present
    expect(screen.getByTestId("mock-titlebar")).toBeInTheDocument();

    // Mocked Google login button should be present
    expect(screen.getByTestId("mock-google-login")).toBeInTheDocument();

    // Login link should point to /login
    const loginLink = screen.getByRole("link", { name: /Login/i });
    expect(loginLink).toBeInTheDocument();
    expect(loginLink.getAttribute("href")).toBe("/login");
  });

  test("has accessible structure and actionable elements", () => {
    render(
      <MemoryRouter>
        <RegisterPage />
      </MemoryRouter>,
    );

    // There should be exactly one main Register heading
    const headings = screen.getAllByRole("heading", { name: /Register/i });
    expect(headings.length).toBe(1);

    // Ensure the Google login is a button element (mocked)
    const googleBtn = screen.getByTestId("mock-google-login");
    expect(googleBtn.tagName.toLowerCase()).toBe("button");
  });
});
