import { Link } from "react-router"

import { AuthLayout } from "@/features/auth/components/auth-layout"
import { SignupForm } from "@/features/auth/components/signup-form"
import { paths } from "./paths"

export function SignupPage() {
  return (
    <AuthLayout
      title="Create your account"
      description="It takes a minute. No bank details needed."
      footer={
        <>
          Already have an account?{" "}
          <Link to={paths.login} className="font-medium text-foreground underline underline-offset-4">
            Log in
          </Link>
        </>
      }
    >
      <SignupForm />
    </AuthLayout>
  )
}
