"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

import { useCurrentUser } from "@/hooks/use-current-user"
import { AppShell } from "@/components/layout/app-shell"
import { Skeleton } from "@/components/ui/skeleton"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const { data: user, isLoading, isError } = useCurrentUser()

  useEffect(() => {
    if (!isLoading && (isError || !user)) {
      router.replace("/sign-in")
    }
  }, [isLoading, isError, user, router])

  if (isLoading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Skeleton className="h-8 w-48" />
      </div>
    )
  }

  return <AppShell user={user}>{children}</AppShell>
}
