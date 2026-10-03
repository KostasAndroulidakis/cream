import { RouterProvider } from "react-router"

import { Toaster } from "@/components/ui/sonner"
import { router } from "@/routes/router"

function App() {
  return (
    <>
      <RouterProvider router={router} />
      {/* One place for notifications, whatever the page */}
      <Toaster />
    </>
  )
}

export default App
