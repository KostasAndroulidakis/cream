import { FormAlert } from "@/components/form-alert"
import { Button } from "@/components/ui/button"
import { DialogDescription, DialogTitle } from "@/components/ui/dialog"
import { useStartConnection, type Aspsp } from "@/features/bank/api"
import { ENABLE_BANKING_PRIVACY_URL, ENABLE_BANKING_TERMS_URL } from "@/features/bank/countries"
import { BankLogo } from "@/features/bank/components/bank-logo"
import { userMessage } from "@/lib/api/errors"

// The service CREAM reaches banks through, where Monarch names Plaid
const PROVIDER = "Enable Banking"
const LINK = "underline underline-offset-2 hover:text-foreground"

/**
 * Monarch's "Monarch uses Plaid to connect your accounts", for Enable Banking:
 * who connects the bank, what CREAM gets, and Continue to log in on the bank's own page.
 */
export function ConsentStep({ bank }: { bank: Aspsp }) {
  const startConnection = useStartConnection()

  return (
    <div className="flex flex-col">
      <p className="pt-6 text-center text-sm font-semibold tracking-[0.12em] uppercase">{PROVIDER}</p>

      <div className="space-y-6 px-8 pt-8 pb-10">
        <div className="flex -space-x-2" aria-hidden>
          <span className="grid size-14 place-items-center rounded-2xl bg-primary text-xl font-semibold text-primary-foreground">
            C
          </span>
          <BankLogo name={bank.name} logo={bank.logo} className="size-14 rounded-2xl border-2 border-card" />
        </div>
        <DialogTitle className="text-3xl leading-tight font-medium tracking-tight">
          CREAM uses {PROVIDER} to connect your accounts
        </DialogTitle>
        <DialogDescription className="text-base text-muted-foreground">
          You'll log in on {bank.name}'s own page and choose the accounts CREAM may read. CREAM never sees your bank
          password, and access lasts up to 180 days before you reconnect.
        </DialogDescription>
        {startConnection.isError && <FormAlert message={userMessage(startConnection.error)} />}
      </div>

      <div className="space-y-4 rounded-b-xl border-t bg-muted/40 px-8 py-6">
        <p className="text-sm text-muted-foreground">
          <a href={ENABLE_BANKING_TERMS_URL} target="_blank" rel="noreferrer" className={LINK}>
            Terms
          </a>{" "}
          apply. By continuing, you agree to {PROVIDER}'s{" "}
          <a href={ENABLE_BANKING_PRIVACY_URL} target="_blank" rel="noreferrer" className={LINK}>
            Privacy Policy
          </a>
          .
        </p>
        <Button
          size="lg"
          className="h-14 w-full rounded-xl text-base"
          disabled={startConnection.isPending}
          onClick={() => startConnection.mutate({ aspsp_name: bank.name, country: bank.country })}
        >
          {startConnection.isPending ? `Opening ${bank.name}…` : "Continue"}
        </Button>
      </div>
    </div>
  )
}
