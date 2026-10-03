import { Button } from "@/components/ui/button"

/** "Add manual account", centered under the lists of the Add account dialog. */
export function AddManualButton({ onClick }: { onClick: () => void }) {
  return (
    <div className="flex justify-center pt-4">
      <Button variant="outline" size="lg" className="h-11 w-64 text-base" onClick={onClick}>
        Add manual account
      </Button>
    </div>
  )
}
