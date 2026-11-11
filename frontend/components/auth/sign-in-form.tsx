"use client"

import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { authService } from "@/services/auth"
import { ApiError } from "@/lib/api-client"
import { signInSchema, type SignInInput } from "@/schemas/auth"

export function SignInForm() {
  const router = useRouter()
  const queryClient = useQueryClient()

  const form = useForm<SignInInput>({
    resolver: zodResolver(signInSchema),
    defaultValues: { email: "", password: "" },
  })

  const signIn = useMutation({
    mutationFn: authService.signIn,
    onSuccess: ({ user }) => {
      queryClient.setQueryData(["current-user"], user)
      router.push("/knowledge-bases")
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Sign in failed.")
    },
  })

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit((values) => signIn.mutate(values))}
        className="flex flex-col gap-4"
        noValidate
      >
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input type="email" autoComplete="email" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input type="password" autoComplete="current-password" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={signIn.isPending} className="mt-2">
          {signIn.isPending ? "Signing in..." : "Sign in"}
        </Button>
      </form>
    </Form>
  )
}
