import { Outlet } from "react-router"

import { Sidebar } from "./sidebar"
import { TopBar } from "./top-bar"

/** Shell for every signed-in page: sidebar on desktop, top bar on smaller screens. */
export function AppLayout() {
  return (
    <div className="flex min-h-svh bg-sidebar">
      <Sidebar />
      <div className="min-w-0 flex-1">
        <TopBar />
        <main className="max-w-6xl px-4 py-8 sm:px-6 lg:py-6 lg:pr-6 lg:pl-2">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
