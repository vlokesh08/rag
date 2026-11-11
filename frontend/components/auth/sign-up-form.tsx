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
import { signUpSchema, type SignUpInput } from "@/schemas/auth"

export function SignUpForm() {
  const router = useRouter()
  const queryClient = useQueryClient()

  const form = useForm<SignUpInput>({
    resolver: zodResolver(signUpSchema),
    defaultValues: { email: "", password: "" },
  })

  const signUp = useMutation({
    mutationFn: authService.signUp,
    onSuccess: ({ user }) => {
      queryClient.setQueryData(["current-user"], user)
      router.push("/knowledge-bases")
    },
    onError: (error) => {
      toast.error(error instanceof ApiError ? error.message : "Sign up failed.")
    },
  })

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit((values) => signUp.mutate(values))}
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
                <Input type="password" autoComplete="new-password" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={signUp.isPending} className="mt-2">
          {signUp.isPending ? "Creating account..." : "Create account"}
        </Button>
      </form>
    </Form>
  )
}
