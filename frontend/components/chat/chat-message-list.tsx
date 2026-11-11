import { Skeleton } from "@/components/ui/skeleton"
import type { Message } from "@/lib/types"
import { ChatMessage } from "@/components/chat/chat-message"

export function ChatMessageList({
  messages,
  isLoading,
  streamingContent,
}: {
  messages: Message[] | undefined
  isLoading: boolean
  streamingContent: string
}) {
  if (isLoading) {
    return (
      <div className="flex flex-col gap-3">
        <Skeleton className="h-10 w-2/3" />
        <Skeleton className="ml-auto h-10 w-1/2" />
      </div>
    )
  }

  const hasMessages = messages && messages.length > 0

  return (
    <div className="flex flex-col gap-3">
      {!hasMessages && !streamingContent && (
        <p className="text-sm text-muted-foreground">
          Ask a question to start the conversation.
        </p>
      )}
      {messages?.map((message) => <ChatMessage key={message.id} message={message} />)}
      {streamingContent && (
        <ChatMessage
          message={{
            id: "streaming",
            conversation_id: "",
            role: "assistant",
            content: streamingContent,
            status: "complete",
            model: null,
            input_tokens: null,
            output_tokens: null,
            latency_ms: null,
            created_at: new Date().toISOString(),
          }}
        />
      )}
    </div>
  )
}
