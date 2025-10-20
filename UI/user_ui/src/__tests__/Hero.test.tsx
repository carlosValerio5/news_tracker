import { render, screen, within, waitFor } from "@testing-library/react";
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

import Landing from "../Landing";

describe("Hero component", () => {
  test("renders heading, paragraph, register button (mocked) and image", async () => {
    const { container } = render(
      <MemoryRouter>
        <Landing />
      </MemoryRouter>,
    );

    // Wait for LatestNewsSection async effect to finish to avoid act(...) warnings
    await waitFor(() =>
      expect(
        screen.queryByText(/Loading latest news.../i),
      ).not.toBeInTheDocument(),
    );

    // Heading
    expect(
      screen.getByRole("heading", {
        name: /Stay Tuned With Zero Manual Effort/i,
      }),
    ).toBeInTheDocument();

    // Paragraph
    expect(
      screen.getByText(/Register to be notified about the latest news./i),
    ).toBeInTheDocument();

    // Mocked RegisterButton inside the Hero section is rendered and receives the props
    const heroSection = screen.getByLabelText("Hero");
    const register = within(heroSection).getByTestId("mock-register");
    expect(register).toBeInTheDocument();
    // The mock spreads props to the anchor so we can inspect them
    expect(register.getAttribute("type")).toBe("PRIMARY");
    // If a class attribute was passed, ensure it includes the expected spacing class
    const classAttr =
      register.getAttribute("class") ??
      register.getAttribute("className") ??
      "";
    if (classAttr) {
      expect(classAttr).toContain("ml-3");
    }

    // The landing page background should be an image (decorative fixed element)
    const background = container.querySelector(
      'div[aria-hidden="true"].fixed',
    ) as HTMLElement | null;
    expect(background).toBeTruthy();
    // inline style should contain a url(...) string when the background is set
    expect(background?.style.backgroundImage).toMatch(/url\(/);
  });
});
