import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import AuthenticationFailed from "../core/AuthenticationFailed";

describe("AuthenticationFailed", () => {
  it("renders failure message and login link", () => {
    render(
      <MemoryRouter>
        <AuthenticationFailed />
      </MemoryRouter>,
    );
    expect(screen.getByText(/Authentication Failed/i)).toBeInTheDocument();
    expect(
      screen.getByText(/Please check your credentials/i),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /Go to Login/i }),
    ).toBeInTheDocument();
  });
});
