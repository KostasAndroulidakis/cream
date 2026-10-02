import { createBrowserRouter, Navigate } from "react-router"

import { RedirectIfAuthenticated, RequireAuth } from "./guards"
import { HomePage } from "./home-page"
import { LoginPage } from "./login-page"
import { paths } from "./paths"
import { SignupPage } from "./signup-page"

export const router = createBrowserRouter([
  {
    element: <RequireAuth />,
    children: [{ path: paths.home, element: <HomePage /> }],
  },
  {
    element: <RedirectIfAuthenticated />,
    children: [
      { path: paths.login, element: <LoginPage /> },
      { path: paths.signup, element: <SignupPage /> },
    ],
  },
  { path: "*", element: <Navigate to={paths.home} replace /> },
])
