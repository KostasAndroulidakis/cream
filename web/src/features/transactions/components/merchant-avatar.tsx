/** A round mark with the merchant's first letter, in place of a logo. */
export function MerchantAvatar({ name }: { name: string }) {
  return (
    <span
      aria-hidden
      className="grid size-7 shrink-0 place-items-center rounded-full bg-muted text-xs font-semibold text-muted-foreground uppercase"
    >
      {name.trim().charAt(0)}
    </span>
  )
}
