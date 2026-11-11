"use client"

import { useRouter } from "next/navigation"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { useConversations, useCreateConversation } from "@/hooks/use-conversations"

export default function ChatIndexPage() {
  const router = useRouter()
  const { data: conversations, isLoading } = useConversations()
  const createConversation = useCreateConversation()

  function handleNewConversation() {
    createConversation.mutate(
      {},
      {
        onSuccess: (conversation) => {
          router.push(`/chat/${conversation.id}`)
        },
      }
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Conversations</h1>
        <Button onClick={handleNewConversation} disabled={createConversation.isPending}>
          New conversation
        </Button>
      </div>

      {isLoading && <Skeleton className="h-20 w-full" />}

      {!isLoading && (!conversations || conversations.length === 0) && (
        <p className="text-sm text-muted-foreground">
          No conversations yet. Start one to begin chatting.
        </p>
      )}

      <div className="flex flex-col gap-2">
        {conversations?.map((conversation) => (
          <Card
            key={conversation.id}
            className="cursor-pointer transition-colors hover:bg-muted/50"
            onClick={() => router.push(`/chat/${conversation.id}`)}
          >
            <CardHeader>
              <CardTitle className="text-sm font-medium">
                {conversation.title ?? "Untitled conversation"}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground">
              Created {new Date(conversation.created_at).toLocaleString()}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
