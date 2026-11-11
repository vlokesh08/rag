"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { useKnowledgeBases } from "@/hooks/use-knowledge-bases"

export function KbList() {
  const { data: knowledgeBases, isLoading, isError } = useKnowledgeBases()

  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-28 rounded-lg" />
        ))}
      </div>
    )
  }

  if (isError) {
    return <p className="text-sm text-destructive">Could not load knowledge bases.</p>
  }

  if (!knowledgeBases || knowledgeBases.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        No knowledge bases yet. Create one to get started.
      </p>
    )
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {knowledgeBases.map((kb) => (
        <Card key={kb.id}>
          <CardHeader>
            <CardTitle>{kb.name}</CardTitle>
            {kb.description && <CardDescription>{kb.description}</CardDescription>}
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground">
            Created {new Date(kb.created_at).toLocaleDateString()}
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
