import { useEffect, useRef, useState } from "react"
import { Popover } from "@base-ui/react/popover"

import { cn } from "@/lib/utils"

type EmojiPickerProps = {
  value: string | null
  onChange: (emoji: string) => void
  // Shown until an emoji is picked, as Monarch does
  placeholder: string
  className?: string
}

/**
 * The icon button of "Icon & Name": opens emoji-mart's picker (Monarch uses the same one) below it.
 * The picker and its emoji data load only on first open, so they don't weigh on every page.
 */
export function EmojiPicker({ value, onChange, placeholder, className }: EmojiPickerProps) {
  const [open, setOpen] = useState(false)

  return (
    <Popover.Root open={open} onOpenChange={setOpen}>
      <Popover.Trigger
        type="button"
        aria-label={value ? `Icon: ${value}. Change icon` : "Choose an icon"}
        className={cn(
          "grid w-12 shrink-0 place-items-center text-xl outline-none focus-visible:ring-3 focus-visible:ring-ring/50 data-popup-open:ring-1 data-popup-open:ring-ring",
          className,
        )}
      >
        <span aria-hidden>{value ?? placeholder}</span>
      </Popover.Trigger>
      <Popover.Portal>
        <Popover.Positioner side="bottom" align="start" sideOffset={8} className="z-50">
          <Popover.Popup className="outline-none">
            <PickerMount
              onSelect={(emoji) => {
                onChange(emoji)
                setOpen(false)
              }}
            />
          </Popover.Popup>
        </Popover.Positioner>
      </Popover.Portal>
    </Popover.Root>
  )
}

type EmojiSelection = { native: string }

function PickerMount({ onSelect }: { onSelect: (emoji: string) => void }) {
  const container = useRef<HTMLDivElement>(null)
  // The picker is created once; the latest callback is read through the ref
  const onSelectRef = useRef(onSelect)
  useEffect(() => {
    onSelectRef.current = onSelect
  })

  useEffect(() => {
    let picker: HTMLElement | undefined
    let cancelled = false
    void Promise.all([import("emoji-mart"), import("@emoji-mart/data")]).then(([{ Picker }, data]) => {
      if (cancelled || !container.current) return
      picker = new Picker({
        data: data.default,
        onEmojiSelect: (emoji: EmojiSelection) => onSelectRef.current(emoji.native),
        theme: "auto",
        previewPosition: "none",
        skinTonePosition: "search",
        autoFocus: true,
      }) as unknown as HTMLElement
      container.current.appendChild(picker)
    })
    return () => {
      cancelled = true
      picker?.remove()
    }
  }, [])

  return <div ref={container} className="min-h-[435px] min-w-[352px] rounded-xl shadow-lg" />
}
