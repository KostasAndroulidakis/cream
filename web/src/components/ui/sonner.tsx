import { Toaster as Sonner, type ToasterProps } from "sonner"

/**
 * App notifications, styled like Monarch's: a dark card at the bottom right with a title, a short
 * description and a DISMISS action behind a divider. Colors come from the theme tokens.
 */
const Toaster = (props: ToasterProps) => (
  <Sonner
    position="bottom-right"
    toastOptions={{
      unstyled: true,
      classNames: {
        toast: "flex w-[min(24rem,calc(100vw-2rem))] items-stretch overflow-hidden rounded-lg bg-foreground text-background shadow-lg",
        content: "flex-1 space-y-1 px-5 py-4",
        title: "text-sm font-semibold",
        description: "text-sm text-background/70",
        actionButton:
          "shrink-0 cursor-pointer border-l border-background/15 px-5 text-xs font-semibold tracking-widest text-background/80 uppercase transition-colors hover:text-background",
      },
    }}
    {...props}
  />
)

export { Toaster }
