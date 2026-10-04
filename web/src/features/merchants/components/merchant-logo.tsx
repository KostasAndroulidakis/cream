import { RoundLogo } from "@/components/round-logo"
import { logoUrl } from "../logo"

type MerchantLogoProps = {
  name: string
  // The merchant's website (its own or a known merchant's); none = the initial
  website?: string | null
  className?: string
}

/** A merchant's logo from its website, or its initial, as Monarch shows merchants. */
export function MerchantLogo({ name, website, className }: MerchantLogoProps) {
  return <RoundLogo name={name} src={website ? logoUrl(website) : null} className={className} />
}
