import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"

import { FormAlert } from "@/components/form-alert"
import { FormField } from "@/components/form-field"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { userMessage } from "@/lib/api/errors"
import { fieldA11y } from "@/lib/forms"
import { useLogin } from "../api"
import { loginSchema, type LoginValues } from "../schemas"

export function LoginForm() {
  const login = useLogin()
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { username: "", password: "" },
  })

  return (
    <form onSubmit={handleSubmit((values) => login.mutate(values))} noValidate className="space-y-4">
      {login.isError && <FormAlert message={userMessage(login.error)} />}

      <FormField id="username" label="Username" error={errors.username?.message}>
        <Input
          id="username"
          autoComplete="username"
          autoFocus
          {...fieldA11y("username", errors.username?.message)}
          {...register("username")}
        />
      </FormField>

      <FormField id="password" label="Password" error={errors.password?.message}>
        <Input
          id="password"
          type="password"
          autoComplete="current-password"
          {...fieldA11y("password", errors.password?.message)}
          {...register("password")}
        />
      </FormField>

      <Button type="submit" size="lg" className="w-full" disabled={login.isPending}>
        {login.isPending ? "Logging in…" : "Log in"}
      </Button>
    </form>
  )
}
