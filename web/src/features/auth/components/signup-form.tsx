import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"

import { FormAlert } from "@/components/form-alert"
import { FormField } from "@/components/form-field"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { userMessage } from "@/lib/api/errors"
import { fieldA11y } from "@/lib/forms"
import { useSignup } from "../api"
import { signupSchema, type SignupValues } from "../schemas"

type FieldConfig = {
  name: keyof SignupValues
  label: string
  type?: string
  autoComplete: string
}

const NAME_FIELDS: FieldConfig[] = [
  { name: "first_name", label: "First name", autoComplete: "given-name" },
  { name: "last_name", label: "Last name", autoComplete: "family-name" },
]

const ACCOUNT_FIELDS: FieldConfig[] = [
  { name: "username", label: "Username", autoComplete: "username" },
  { name: "email", label: "Email", type: "email", autoComplete: "email" },
  { name: "password", label: "Password", type: "password", autoComplete: "new-password" },
]

export function SignupForm() {
  const signup = useSignup()
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignupValues>({
    resolver: zodResolver(signupSchema),
    defaultValues: { first_name: "", last_name: "", username: "", email: "", password: "" },
  })

  const renderField = ({ name, label, type, autoComplete }: FieldConfig) => {
    const error = errors[name]?.message
    return (
      <FormField key={name} id={name} label={label} error={error}>
        <Input id={name} type={type} autoComplete={autoComplete} {...fieldA11y(name, error)} {...register(name)} />
      </FormField>
    )
  }

  return (
    <form onSubmit={handleSubmit((values) => signup.mutate(values))} noValidate className="space-y-4">
      {signup.isError && <FormAlert message={userMessage(signup.error)} />}

      <div className="grid gap-4 sm:grid-cols-2">{NAME_FIELDS.map(renderField)}</div>
      {ACCOUNT_FIELDS.map(renderField)}

      <Button type="submit" size="lg" className="w-full" disabled={signup.isPending}>
        {signup.isPending ? "Creating account…" : "Create account"}
      </Button>
    </form>
  )
}
