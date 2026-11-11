export type User = {
  id: string
  email: string
  created_at: string
}

export type KnowledgeBase = {
  id: string
  name: string
  description: string | null
  created_at: string
  updated_at: string
}

export type Conversation = {
  id: string
  title: string | null
  knowledge_base_id: string | null
  created_at: string
  updated_at: string
}

export type MessageRole = "user" | "assistant" | "system"
export type MessageStatus = "complete" | "error"

export type Message = {
  id: string
  conversation_id: string
  role: MessageRole
  content: string
  status: MessageStatus
  model: string | null
  input_tokens: number | null
  output_tokens: number | null
  latency_ms: number | null
  created_at: string
}
