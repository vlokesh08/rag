import { useQuery } from "@tanstack/react-query"

import { ApiError } from "@/lib/api-client"
import { authService } from "@/services/auth"

export function useCurrentUser() {
  return useQuery({
    queryKey: ["current-user"],
    queryFn: authService.me,
    retry: false,
    throwOnError: (error) => !(error instanceof ApiError && error.status === 401),
  })
}
