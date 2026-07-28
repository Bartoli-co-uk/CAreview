import { afterEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AppStateProvider } from "../state/appState";
import { SignIn } from "../pages/SignIn";

function renderSignIn() {
  return render(
    <AppStateProvider>
      <SignIn />
    </AppStateProvider>,
  );
}

afterEach(() => {
  vi.unstubAllGlobals();
});

// Frontend analogue of tests/test_ui_safety.py's AppOnlyModeToggleTests: the
// app-only client secret must never linger past a submit attempt, whether it
// succeeds, fails, or the request itself throws — same safety property, new
// stack (component state instead of a raw DOM input value).
describe("SignIn app-only secret handling", () => {
  it("clears the secret field after a request that rejects (network failure)", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("network down")));
    const user = userEvent.setup();
    renderSignIn();

    await user.click(screen.getByText("Use app-only sign-in (advanced)"));
    await user.type(screen.getByLabelText(/Tenant ID or domain/), "contoso.onmicrosoft.com");
    await user.type(screen.getByLabelText(/Client \(application\) ID/), "11111111-1111-1111-1111-111111111111");
    const secretInput = screen.getByLabelText(/Client secret/) as HTMLInputElement;
    await user.type(secretInput, "super-secret-value");
    await user.click(screen.getByText("Sign in with app-only credentials"));

    await waitFor(() => expect(secretInput.value).toBe(""));
  });

  it("clears the secret field when switching back to standard sign-in", async () => {
    const user = userEvent.setup();
    renderSignIn();

    await user.click(screen.getByText("Use app-only sign-in (advanced)"));
    const secretInput = screen.getByLabelText(/Client secret/) as HTMLInputElement;
    await user.type(secretInput, "super-secret-value");
    await user.click(screen.getByText("Back to standard sign-in"));

    await user.click(screen.getByText("Use app-only sign-in (advanced)"));
    expect((screen.getByLabelText(/Client secret/) as HTMLInputElement).value).toBe("");
  });

  it("rejects organizations/common/consumers as an app-only tenant before any request is made", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    const user = userEvent.setup();
    renderSignIn();

    await user.click(screen.getByText("Use app-only sign-in (advanced)"));
    await user.type(screen.getByLabelText(/Tenant ID or domain/), "organizations");
    await user.type(screen.getByLabelText(/Client \(application\) ID/), "11111111-1111-1111-1111-111111111111");
    await user.type(screen.getByLabelText(/Client secret/), "super-secret-value");
    await user.click(screen.getByText("Sign in with app-only credentials"));

    expect(fetchMock).not.toHaveBeenCalled();
    expect(screen.getByText(/organizations\/common\/consumers/)).toBeInTheDocument();
  });

  it("renders the secret input as type=password with autocomplete off", async () => {
    const user = userEvent.setup();
    renderSignIn();
    await user.click(screen.getByText("Use app-only sign-in (advanced)"));
    const secretInput = screen.getByLabelText(/Client secret/) as HTMLInputElement;
    expect(secretInput.type).toBe("password");
    expect(secretInput.autocomplete).toBe("off");
  });
});
