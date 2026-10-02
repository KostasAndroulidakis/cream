import { useState } from "react"
import { useQuery } from "@tanstack/react-query"

import { FormAlert } from "@/components/form-alert"
import { FormField } from "@/components/form-field"
import { NativeSelect } from "@/components/native-select"
import { Button } from "@/components/ui/button"
import { userMessage } from "@/lib/api/errors"
import { aspspsQueryOptions, useStartConnection } from "../api"
import { BANK_COUNTRIES, DEFAULT_BANK_COUNTRY, countryName } from "../countries"

export function ConnectBankForm() {
  const [country, setCountry] = useState<string>(DEFAULT_BANK_COUNTRY)
  const [bankName, setBankName] = useState("")
  const banks = useQuery(aspspsQueryOptions(country))
  const startConnection = useStartConnection()

  const error = banks.error ?? startConnection.error

  return (
    <form
      className="space-y-4"
      onSubmit={(event) => {
        event.preventDefault()
        startConnection.mutate({ aspsp_name: bankName, country })
      }}
    >
      {error && <FormAlert message={userMessage(error)} />}

      <div className="grid gap-4 sm:grid-cols-[12rem_1fr]">
        <FormField id="bank-country" label="Country">
          <NativeSelect
            id="bank-country"
            value={country}
            onChange={(event) => {
              setCountry(event.target.value)
              setBankName("")
            }}
          >
            {BANK_COUNTRIES.map((code) => (
              <option key={code} value={code}>
                {countryName(code)}
              </option>
            ))}
          </NativeSelect>
        </FormField>

        <FormField id="bank-name" label="Bank">
          <NativeSelect
            id="bank-name"
            value={bankName}
            disabled={banks.isPending}
            onChange={(event) => setBankName(event.target.value)}
          >
            <option value="" disabled>
              {banks.isPending ? "Loading banks…" : "Pick your bank"}
            </option>
            {banks.data?.map((bank) => (
              <option key={bank.name} value={bank.name}>
                {bank.name}
              </option>
            ))}
          </NativeSelect>
        </FormField>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <Button type="submit" disabled={!bankName || startConnection.isPending}>
          {startConnection.isPending ? "Opening your bank…" : "Continue to your bank"}
        </Button>
        <p className="text-sm text-muted-foreground">
          You'll log in on your bank's own page. CREAM never sees your bank password.
        </p>
      </div>
    </form>
  )
}
