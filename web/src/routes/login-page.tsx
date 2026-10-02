import { Link } from "react-router"

import { AuthLayout } from "@/features/auth/components/auth-layout"
import { LoginForm } from "@/features/auth/components/login-form"
import { paths } from "./paths"

export function LoginPage() {
  return (
    <AuthLayout
      title="Log in"
      description="Pick up where you left off."
      footer={
        <>
          New to CREAM?{" "}
          <Link to={paths.signup} className="font-medium text-foreground underline underline-offset-4">
            Create an account
          </Link>
        </>
      }
    >
      <LoginForm />
    </AuthLayout>
  )
}
