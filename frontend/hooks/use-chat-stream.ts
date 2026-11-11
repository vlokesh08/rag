import { useCallback, useState } from "react"
import { useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import { chatService } from "@/services/chat"

export function useChatStream(conversationId: string) {
  const queryClient = useQueryClient()
  const [streamingContent, setStreamingContent] = useState("")
  const [isStreaming, setIsStreaming] = useState(false)

  const sendMessage = useCallback(
    async (content: string) => {
      setIsStreaming(true)
      setStreamingContent("")

      try {
        await chatService.send(conversationId, content, (event) => {
          if (event.event === "content_delta") {
            const { delta } = JSON.parse(event.data) as { delta: string }
            setStreamingContent((prev) => prev + delta)
          } else if (event.event === "message_complete") {
            queryClient.invalidateQueries({
              queryKey: ["conversations", conversationId, "messages"],
            })
          } else if (event.event === "error") {
            const { message } = JSON.parse(event.data) as { message: string }
            toast.error(message)
            queryClient.invalidateQueries({
              queryKey: ["conversations", conversationId, "messages"],
            })
          }
        })
      } catch {
        toast.error("Could not reach the assistant. Please try again.")
      } finally {
        setIsStreaming(false)
        setStreamingContent("")
      }
    },
    [conversationId, queryClient]
  )

  return { sendMessage, streamingContent, isStreaming }
}
