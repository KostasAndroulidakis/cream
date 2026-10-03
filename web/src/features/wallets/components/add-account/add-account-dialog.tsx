import { useState } from "react"
import { Plus } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog"
import type { Aspsp } from "@/features/bank/api"
import { cn } from "@/lib/utils"
import type { WalletType } from "../../api"
import { useAccountTypes } from "../../use-account-types"
import { addFormLabel } from "../../wallet-types"
import { CreateWalletForm } from "../create-wallet-form"
import { BankListStep } from "./bank-list-step"
import { ConsentStep } from "./consent-step"
import { ManualTypesStep } from "./manual-types-step"
import { StartStep } from "./start-step"
import { StepHeader } from "./step-header"

type Step =
  | { kind: "start" }
  | { kind: "banks"; query: string }
  | { kind: "consent"; bank: Aspsp }
  | { kind: "manual" }
  | { kind: "form"; type: WalletType }

const START: Step = { kind: "start" }
// Monarch's width; the close button lines up with the title
const CONTENT_CLASS =
  "gap-0 p-0 sm:max-w-[34rem] [&>[data-slot=dialog-close]]:top-5 [&>[data-slot=dialog-close]]:right-5"
// The provider's consent screen is narrower, like Plaid's window
const CONSENT_WIDTH = "sm:max-w-[28rem]"

/**
 * Monarch's "Add account", the same everywhere (Accounts, Dashboard, Settings › Institutions):
 * the ways to add one → connect a bank, or Add Manual Account → its type → the account's details.
 */
export function AddAccountDialog() {
  const [open, setOpen] = useState(false)
  const [step, setStep] = useState<Step>(START)
  const { catalog } = useAccountTypes()
  const formType = step.kind === "form" ? catalog.find((info) => info.type === step.type) : undefined

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
      <DialogContent className={cn(CONTENT_CLASS, step.kind === "consent" && CONSENT_WIDTH)}>
        {step.kind === "start" && (
          <>
            <StepHeader title="Add an account" description="Connect a bank or add an account by hand." />
            <StartStep
              onSearch={(query) => setStep({ kind: "banks", query })}
              onConnectBank={() => setStep({ kind: "banks", query: "" })}
              onAddManual={() => setStep({ kind: "manual" })}
            />
          </>
        )}
        {step.kind === "banks" && (
          <>
            <StepHeader
              title="Banks & credit cards"
              description="Find your bank, then log in on its own page."
              onBack={() => setStep(START)}
            />
            <BankListStep
              initialQuery={step.query}
              onPick={(bank) => setStep({ kind: "consent", bank })}
              onAddManual={() => setStep({ kind: "manual" })}
            />
          </>
        )}
        {step.kind === "consent" && <ConsentStep bank={step.bank} />}
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
        {formType && (
          <>
            <StepHeader
              title={`Add ${addFormLabel(formType.type, formType.label)} Account`}
              description="The account's name, kind and what's in it today."
              onBack={() => setStep({ kind: "manual" })}
            />
            <CreateWalletForm
              typeInfo={formType}
              onCreated={() => onOpenChange(false)}
              onCancel={() => onOpenChange(false)}
            />
          </>
        )}
      </DialogContent>
    </Dialog>
  )
}
