import { apiClient } from "@/lib/api-client"
import type { User } from "@/lib/types"
import type { SignInInput, SignUpInput } from "@/schemas/auth"

export const authService = {
  signUp: (input: SignUpInput) => apiClient.post<{ user: User }>("/api/v1/auth/sign-up", input),
  signIn: (input: SignInInput) => apiClient.post<{ user: User }>("/api/v1/auth/sign-in", input),
  signOut: () => apiClient.post<void>("/api/v1/auth/sign-out"),
  me: () => apiClient.get<User>("/api/v1/auth/me"),
}
