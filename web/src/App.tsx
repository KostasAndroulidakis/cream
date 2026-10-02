import { SystemStatus } from "@/features/health/components/system-status"

function App() {
  return (
    <main className="grid min-h-svh place-items-center bg-muted/40 p-6">
      <div className="w-full max-w-sm space-y-6">
        <header className="space-y-1 text-center">
          <h1 className="text-3xl font-semibold tracking-tight">CREAM</h1>
          <p className="text-sm text-muted-foreground">Cash Rules Everything Around Me</p>
        </header>
        <SystemStatus />
      </div>
    </main>
  )
}

export default App
