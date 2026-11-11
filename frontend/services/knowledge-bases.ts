import { apiClient } from "@/lib/api-client"
import type { KnowledgeBase } from "@/lib/types"
import type { CreateKnowledgeBaseInput } from "@/schemas/knowledge-base"

export const knowledgeBaseService = {
  list: () => apiClient.get<KnowledgeBase[]>("/api/v1/knowledge-bases"),
  create: (input: CreateKnowledgeBaseInput) =>
    apiClient.post<KnowledgeBase>("/api/v1/knowledge-bases", input),
  get: (id: string) => apiClient.get<KnowledgeBase>(`/api/v1/knowledge-bases/${id}`),
  delete: (id: string) => apiClient.delete<void>(`/api/v1/knowledge-bases/${id}`),
}
