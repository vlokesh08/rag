"use client"

import { useState } from "react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            retry: 1,
            // Every query in this app depends on the browser-only session
            // cookie, so none of them can run during the server render pass
            // of a client component (the Next.js server process never has
            // that cookie, so it would always see an unauthenticated 401).
            enabled: typeof window !== "undefined",
          },
        },
      })
  )

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
}
