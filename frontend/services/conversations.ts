import { apiClient } from "@/lib/api-client"
import type { Conversation, Message } from "@/lib/types"

export const conversationService = {
  list: () => apiClient.get<Conversation[]>("/api/v1/conversations"),
  create: (input: { title?: string; knowledge_base_id?: string }) =>
    apiClient.post<Conversation>("/api/v1/conversations", input),
  get: (id: string) => apiClient.get<Conversation>(`/api/v1/conversations/${id}`),
  delete: (id: string) => apiClient.delete<void>(`/api/v1/conversations/${id}`),
  listMessages: (id: string) => apiClient.get<Message[]>(`/api/v1/conversations/${id}/messages`),
}
