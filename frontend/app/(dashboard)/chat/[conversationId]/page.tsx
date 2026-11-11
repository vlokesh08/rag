"use client"

import { use } from "react"

import { ChatComposer } from "@/components/chat/chat-composer"
import { ChatMessageList } from "@/components/chat/chat-message-list"
import { useChatStream } from "@/hooks/use-chat-stream"
import { useConversationMessages } from "@/hooks/use-conversations"

export default function ChatConversationPage({
  params,
}: {
  params: Promise<{ conversationId: string }>
}) {
  const { conversationId } = use(params)
  const { data: messages, isLoading } = useConversationMessages(conversationId)
  const { sendMessage, streamingContent, isStreaming } = useChatStream(conversationId)

  return (
    <div className="mx-auto flex h-[calc(100vh-8rem)] max-w-2xl flex-col gap-4">
      <div className="flex-1 overflow-y-auto">
        <ChatMessageList
          messages={messages}
          isLoading={isLoading}
          streamingContent={streamingContent}
        />
      </div>
      <ChatComposer onSend={sendMessage} disabled={isStreaming} />
    </div>
  )
}
