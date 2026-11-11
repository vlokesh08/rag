import { API_URL } from "@/lib/api-client"

export type SSEEvent = {
  event: string
  data: string
}

function parseEventBlock(block: string): SSEEvent | null {
  const lines = block.split("\n")
  let event = "message"
  const dataLines: string[] = []

  for (const line of lines) {
    if (line.startsWith("event:")) {
      event = line.slice("event:".length).trim()
    } else if (line.startsWith("data:")) {
      dataLines.push(line.slice("data:".length).trim())
    }
  }

  if (dataLines.length === 0) return null
  return { event, data: dataLines.join("\n") }
}

/**
 * EventSource can't send a POST body, so SSE over a POST endpoint has to be
 * parsed by hand from the fetch Response's ReadableStream.
 */
export async function postSSE(
  path: string,
  body: unknown,
  onEvent: (event: SSEEvent) => void,
  signal?: AbortSignal
): Promise<void> {
  const response = await fetch(`${API_URL}${path}`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  })

  if (!response.ok || !response.body) {
    throw new Error(`Chat request failed with ${response.status}`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ""

  for (;;) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const blocks = buffer.split("\n\n")
    buffer = blocks.pop() ?? ""

    for (const block of blocks) {
      if (!block.trim()) continue
      const parsed = parseEventBlock(block)
      if (parsed) onEvent(parsed)
    }
  }
}
