import { createBrowserRouter, Navigate } from "react-router"

import { AccountsPage } from "./accounts-page"
import { AppLayout } from "./app-layout"
import { ConnectionCallbackPage } from "./connection-callback-page"
import { RedirectIfAuthenticated, RequireAuth } from "./guards"
import { HomePage } from "./home-page"
import { LoginPage } from "./login-page"
import { paths } from "./paths"
import { ReviewPage } from "./review-page"
import { SettingsCategoriesPage } from "./settings-categories-page"
import { SettingsInstitutionsPage } from "./settings-institutions-page"
import { SettingsLayout } from "./settings-layout"
import { SettingsProfilePage } from "./settings-profile-page"
import { SignupPage } from "./signup-page"
import { TransactionsPage } from "./transactions-page"

export const router = createBrowserRouter([
  {
    element: <RequireAuth />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { path: paths.home, element: <HomePage /> },
          { path: paths.accounts, element: <AccountsPage /> },
          { path: paths.transactions, element: <TransactionsPage /> },
          { path: paths.review, element: <ReviewPage /> },
          { path: paths.connections, element: <Navigate to={paths.settingsInstitutions} replace /> },
          {
            path: paths.settings,
            element: <SettingsLayout />,
            children: [
              // Settings opens on Profile, like Monarch
              { index: true, element: <Navigate to={paths.settingsProfile} replace /> },
              { path: paths.settingsProfile, element: <SettingsProfilePage /> },
              { path: paths.settingsInstitutions, element: <SettingsInstitutionsPage /> },
              { path: paths.settingsCategories, element: <SettingsCategoriesPage /> },
            ],
          },
        ],
      },
      // Full-screen: the user lands here straight from the bank's site
      { path: paths.connectionCallback, element: <ConnectionCallbackPage /> },
    ],
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
