import { useEffect, useRef } from "react"
import { Link, Navigate, useSearchParams } from "react-router"

import { FullPageMessage } from "@/components/full-page-message"
import { useCompleteConnection } from "@/features/bank/api"
import { userMessage } from "@/lib/api/errors"
import { paths } from "./paths"

/** The bank sends the user back here with ?code=…&state=… (or ?error=…). */
export function ConnectionCallbackPage() {
  const [params] = useSearchParams()
  const completeConnection = useCompleteConnection()
  const code = params.get("code")
  const state = params.get("state")
  // The code works once; StrictMode runs effects twice in development, so guard it
  const submitted = useRef(false)

  useEffect(() => {
    if (!code || !state || submitted.current) return
    submitted.current = true
    completeConnection.mutate({ code, state })
  }, [code, state, completeConnection])

  if (completeConnection.isSuccess) return <Navigate to={paths.connections} replace />

  const failed = !code || !state || completeConnection.isError
  if (failed) {
    const reason = completeConnection.isError
      ? userMessage(completeConnection.error)
      : params.get("error_description") ?? "The bank didn't complete the connection."
    return (
      <FullPageMessage title="Couldn't connect the bank">
        <p className="text-sm text-muted-foreground">{reason}</p>
        <Link to={paths.connections} className="text-sm font-medium underline underline-offset-4">
          Back to banks
        </Link>
      </FullPageMessage>
    )
  }

  return <FullPageMessage title="Finishing the connection…" />
}
