"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"

import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { sendMessageSchema, type SendMessageInput } from "@/schemas/chat"

export function ChatComposer({
  onSend,
  disabled,
}: {
  onSend: (content: string) => void
  disabled: boolean
}) {
  const form = useForm<SendMessageInput>({
    resolver: zodResolver(sendMessageSchema),
    defaultValues: { content: "" },
  })

  function onSubmit(values: SendMessageInput) {
    onSend(values.content)
    form.reset()
  }

  return (
    <form
      onSubmit={form.handleSubmit(onSubmit)}
      className="flex items-end gap-2 border-t pt-4"
    >
      <Textarea
        placeholder="Ask a question..."
        rows={2}
        disabled={disabled}
        {...form.register("content")}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault()
            form.handleSubmit(onSubmit)()
          }
        }}
      />
      <Button type="submit" disabled={disabled}>
        Send
      </Button>
    </form>
  )
}
