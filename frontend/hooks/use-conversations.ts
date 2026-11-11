import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { conversationService } from "@/services/conversations"

export function useConversations() {
  return useQuery({
    queryKey: ["conversations"],
    queryFn: conversationService.list,
  })
}

export function useConversationMessages(conversationId: string | undefined) {
  return useQuery({
    queryKey: ["conversations", conversationId, "messages"],
    queryFn: () => conversationService.listMessages(conversationId!),
    enabled: typeof window !== "undefined" && !!conversationId,
  })
}

export function useCreateConversation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (input: { title?: string; knowledge_base_id?: string } = {}) =>
      conversationService.create(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["conversations"] })
    },
  })
}
