import { useState } from "react"
import { Plus } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog"
import { ConnectBankForm } from "@/features/bank/components/connect-bank-form"
import type { WalletType } from "../../api"
import { useAccountTypes } from "../../use-account-types"
import { CreateWalletForm } from "../create-wallet-form"
import { ManualTypesStep } from "./manual-types-step"
import { StartStep } from "./start-step"
import { StepHeader } from "./step-header"

type Step = { kind: "start" } | { kind: "bank" } | { kind: "manual" } | { kind: "form"; type: WalletType }

const START: Step = { kind: "start" }
// Monarch's width; the close button lines up with the title
const CONTENT_CLASS =
  "gap-0 p-0 sm:max-w-[34rem] [&>[data-slot=dialog-close]]:top-5 [&>[data-slot=dialog-close]]:right-5"

/**
 * Monarch's "Add account", the same everywhere (Accounts, Dashboard, Settings › Institutions):
 * the ways to add one → connect a bank, or Add Manual Account → its type → the account's details.
 */
export function AddAccountDialog() {
  const [open, setOpen] = useState(false)
  const [step, setStep] = useState<Step>(START)
  const { typeLabel } = useAccountTypes()

  function onOpenChange(next: boolean) {
    setOpen(next)
    // Every opening starts from the first step
    if (!next) setStep(START)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogTrigger render={<Button />}>
        <Plus aria-hidden />
        Add account
      </DialogTrigger>
      <DialogContent className={CONTENT_CLASS}>
        {step.kind === "start" && (
          <>
            <StepHeader title="Add an account" description="Connect a bank or add an account by hand." />
            <StartStep
              onConnectBank={() => setStep({ kind: "bank" })}
              onAddManual={() => setStep({ kind: "manual" })}
            />
          </>
        )}
        {step.kind === "bank" && (
          <>
            <StepHeader
              title="Connect a bank"
              description="Pick your bank, then log in on its own page."
              onBack={() => setStep(START)}
            />
            <div className="px-6 pb-6">
              <ConnectBankForm />
            </div>
          </>
        )}
        {step.kind === "manual" && (
          <>
            <StepHeader
              title="Add Manual Account"
              description="Pick the kind of account."
              onBack={() => setStep(START)}
            />
            <ManualTypesStep onPick={(type) => setStep({ kind: "form", type })} />
          </>
        )}
        {step.kind === "form" && (
          <>
            <StepHeader
              title={typeLabel(step.type)}
              description="The account's name and what's in it today."
              onBack={() => setStep({ kind: "manual" })}
            />
            <div className="px-6 pb-6">
              <CreateWalletForm type={step.type} onCreated={() => onOpenChange(false)} />
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  )
}
