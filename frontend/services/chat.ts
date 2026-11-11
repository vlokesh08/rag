import { postSSE, type SSEEvent } from "@/lib/sse"

export const chatService = {
  send: (conversationId: string, content: string, onEvent: (event: SSEEvent) => void, signal?: AbortSignal) =>
    postSSE("/api/v1/chat", { conversation_id: conversationId, content }, onEvent, signal),
}
