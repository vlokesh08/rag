import { cn } from "cn"
import type { Message } from "@/lib/types"

export function ChatMessage({ message }: { message: Message }) {
  const isUser = message.role === "user"

  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[75%] rounded-lg px-3 py-2 text-sm whitespace-pre-wrap",
          isUser ? "bg-primary text-primary-foreground" : "bg-muted",
          message.status === "error" && "border border-destructive text-destructive"
        )}
      >
        {message.content || (message.status === "error" ? "The assistant failed to respond." : "")}
      </div>
    </div>
  )
}
