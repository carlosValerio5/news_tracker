import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import type { RegisterButtonProps } from "../components/RegisterButton";

// Ensure the project's API mock is available (kept for consistency even if Hero doesn't call it)
import * as mockApi from "../__mocks__/services/api";
jest.mock("../services/api", () => mockApi);

// Mock RegisterButton so we can inspect the props passed by Hero
jest.mock("../components/RegisterButton", () => ({
  __esModule: true,
  default: (props: RegisterButtonProps) => (
    <a data-testid="mock-register" {...props}>
      {props.text ?? "Register"}
    </a>
  ),
  ButtonType: { PRIMARY: "PRIMARY", SECONDARY: "SECONDARY" },
}));

import Hero from "../core/Hero";

describe("Hero component", () => {
  test("renders heading, paragraph, register button (mocked) and image", () => {
    render(
      <MemoryRouter>
        <Hero />
      </MemoryRouter>,
    );

    // Heading
    expect(
      screen.getByRole("heading", { name: /Stay tuned/i }),
    ).toBeInTheDocument();

    // Paragraph
    expect(
      screen.getByText(/Register to be notified about the latest news./i),
    ).toBeInTheDocument();

    // Mocked RegisterButton is rendered and receives the props
    const register = screen.getByTestId("mock-register");
    expect(register).toBeInTheDocument();
    // The mock spreads props to the anchor so we can inspect them
    expect(register.getAttribute("type")).toBe("PRIMARY");
    // className passed from Hero should include the ml-3
    expect(
      register.getAttribute("class") || register.getAttribute("className"),
    ).toContain("ml-3");

    // Image exists with the expected src and alt
    const img = screen.getByAltText("newspaper image") as HTMLImageElement;
    expect(img).toBeInTheDocument();
    expect(img.src).toContain(
      "/src/assets/images/utsav-srestha-HeNrEdA4Zp4-unsplash.jpg",
    );
  });
});
