import { describe, expect, it, vi, beforeEach } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"

import { SignInForm } from "@/components/auth/sign-in-form"
import { authService } from "@/services/auth"

const pushMock = vi.fn()

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: pushMock }),
}))

vi.mock("@/services/auth", () => ({
  authService: {
    signIn: vi.fn(),
  },
}))

function renderWithQueryClient() {
  const queryClient = new QueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      <SignInForm />
    </QueryClientProvider>
  )
}

describe("SignInForm", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("renders email and password fields", () => {
    renderWithQueryClient()

    expect(screen.getByLabelText("Email")).toBeInTheDocument()
    expect(screen.getByLabelText("Password")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Sign in" })).toBeInTheDocument()
  })

  it("shows a validation error for an invalid email instead of submitting", async () => {
    const user = userEvent.setup()
    renderWithQueryClient()

    await user.type(screen.getByLabelText("Email"), "not-an-email")
    await user.type(screen.getByLabelText("Password"), "supersecret1")
    await user.click(screen.getByRole("button", { name: "Sign in" }))

    await waitFor(() => {
      expect(screen.getByText("Enter a valid email address.")).toBeInTheDocument()
    })
    expect(authService.signIn).not.toHaveBeenCalled()
  })

  it("calls authService.signIn with the form values on valid submit", async () => {
    vi.mocked(authService.signIn).mockResolvedValue({
      user: { id: "1", email: "alice@example.com", created_at: "2026-01-01T00:00:00Z" },
    })
    const user = userEvent.setup()
    renderWithQueryClient()

    await user.type(screen.getByLabelText("Email"), "alice@example.com")
    await user.type(screen.getByLabelText("Password"), "supersecret1")
    await user.click(screen.getByRole("button", { name: "Sign in" }))

    await waitFor(() => {
      // TanStack Query v5 calls mutationFn(variables, mutationFnContext), so
      // assert on the payload (first argument) rather than the full call.
      expect(vi.mocked(authService.signIn).mock.calls[0]?.[0]).toEqual({
        email: "alice@example.com",
        password: "supersecret1",
      })
    })
    await waitFor(() => {
      expect(pushMock).toHaveBeenCalledWith("/knowledge-bases")
    })
  })
})
