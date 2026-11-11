import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { knowledgeBaseService } from "@/services/knowledge-bases"
import type { CreateKnowledgeBaseInput } from "@/schemas/knowledge-base"

export function useKnowledgeBases() {
  return useQuery({
    queryKey: ["knowledge-bases"],
    queryFn: knowledgeBaseService.list,
  })
}

export function useCreateKnowledgeBase() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (input: CreateKnowledgeBaseInput) => knowledgeBaseService.create(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-bases"] })
    },
  })
}
