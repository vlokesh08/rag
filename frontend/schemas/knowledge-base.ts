import { z } from "zod"

export const createKnowledgeBaseSchema = z.object({
  name: z.string().min(1, "Name is required.").max(255),
  description: z.string().max(5000).optional(),
})

export type CreateKnowledgeBaseInput = z.infer<typeof createKnowledgeBaseSchema>
