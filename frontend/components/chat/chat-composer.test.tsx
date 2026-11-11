import { describe, expect, it, vi, beforeEach } from "vitest"
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { ChatComposer } from "@/components/chat/chat-composer"

describe("ChatComposer", () => {
  const onSend = vi.fn()

  beforeEach(() => {
    onSend.mockClear()
  })

  it("renders a textarea and a send button", () => {
    render(<ChatComposer onSend={onSend} disabled={false} />)

    expect(screen.getByPlaceholderText("Ask a question...")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Send" })).toBeInTheDocument()
  })

  it("calls onSend with the typed content and clears the textarea on submit", async () => {
    const user = userEvent.setup()
    render(<ChatComposer onSend={onSend} disabled={false} />)

    const textarea = screen.getByPlaceholderText("Ask a question...")
    await user.type(textarea, "Hello there")
    await user.click(screen.getByRole("button", { name: "Send" }))

    expect(onSend).toHaveBeenCalledWith("Hello there")
    expect(textarea).toHaveValue("")
  })

  it("submits on Enter without a newline, but not on Shift+Enter", async () => {
    const user = userEvent.setup()
    render(<ChatComposer onSend={onSend} disabled={false} />)

    const textarea = screen.getByPlaceholderText("Ask a question...")
    await user.type(textarea, "Line one{Shift>}{Enter}{/Shift}Line two")
    expect(onSend).not.toHaveBeenCalled()

    await user.type(textarea, "{Enter}")
    expect(onSend).toHaveBeenCalledWith("Line one\nLine two")
  })

  it("disables the textarea and button while streaming", () => {
    render(<ChatComposer onSend={onSend} disabled={true} />)

    expect(screen.getByPlaceholderText("Ask a question...")).toBeDisabled()
    expect(screen.getByRole("button", { name: "Send" })).toBeDisabled()
  })
})
