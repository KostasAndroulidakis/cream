import { useCurrentUser } from "@/features/auth/api"
import { ProfileForm } from "@/features/profile/components/profile-form"

/** Settings › Profile. */
export function SettingsProfilePage() {
  // RequireAuth renders this only once the user is loaded
  const { data: user } = useCurrentUser()

  return (
    <section aria-labelledby="profile-heading" className="rounded-xl border bg-card shadow-xs">
      <h2 id="profile-heading" className="border-b px-6 py-4 text-lg font-medium tracking-tight">
        Profile
      </h2>
      <div className="px-6 py-6">{user && <ProfileForm user={user} />}</div>
    </section>
  )
}
