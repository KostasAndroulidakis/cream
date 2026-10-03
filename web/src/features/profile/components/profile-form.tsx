import { zodResolver } from "@hookform/resolvers/zod"
import { ChevronDown } from "lucide-react"
import { useForm } from "react-hook-form"

import { COMING_SOON } from "@/components/coming-soon-button"
import { FormAlert } from "@/components/form-alert"
import { FormField } from "@/components/form-field"
import { NativeSelect } from "@/components/native-select"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { displayNameOf, useUpdateProfile, type User } from "@/features/auth/api"
import { userMessage } from "@/lib/api/errors"
import { todayInputValue } from "@/lib/dates"
import { fieldA11y } from "@/lib/forms"
import { notifySuccess } from "@/lib/notify"
import { profileSchema, type ProfileFormInput, type ProfileValues } from "../schemas"
import { BROWSER_TIMEZONE, TIMEZONES } from "../timezones"
import { UserAvatar } from "./user-avatar"

// Monarch's fields are taller than the app's default inputs
const FIELD = "h-10 md:text-[0.9375rem]"

// A zone the browser doesn't list (e.g. "UTC" in some browsers) still needs to show as chosen
function timezoneChoices(current: string): readonly string[] {
  return TIMEZONES.includes(current) ? TIMEZONES : [current, ...TIMEZONES]
}

function formValues(user: User): ProfileFormInput {
  return {
    first_name: user.first_name,
    last_name: user.last_name,
    display_name: user.display_name ?? "",
    birthday: user.birthday ?? "",
    timezone: user.timezone ?? BROWSER_TIMEZONE,
  }
}

/** Settings › Profile: name, display name, birthday and timezone. */
export function ProfileForm({ user }: { user: User }) {
  const updateProfile = useUpdateProfile()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<ProfileFormInput, unknown, ProfileValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: formValues(user),
  })

  const onSubmit = handleSubmit((values) =>
    updateProfile.mutate(values, {
      onSuccess: (saved) => {
        // The saved values become the new starting point, so the button greys out again
        reset(formValues(saved))
        notifySuccess({ title: "Profile updated" })
      },
    }),
  )

  const nameError = errors.first_name?.message ?? errors.last_name?.message

  return (
    <form onSubmit={onSubmit} noValidate className="space-y-5">
      <div className="flex items-center gap-4">
        <UserAvatar name={displayNameOf(user)} />
        <Button
          type="button"
          variant="outline"
          aria-disabled
          title={`Profile photo: ${COMING_SOON.toLowerCase()}`}
          className="cursor-not-allowed"
        >
          Edit
          <ChevronDown aria-hidden />
        </Button>
      </div>

      {updateProfile.isError && <FormAlert message={userMessage(updateProfile.error)} />}

      {/* Monarch has one "Full Name"; CREAM keeps first and last apart, side by side */}
      <FormField id="profile-first-name" label="Full Name" error={nameError}>
        <div className="grid grid-cols-2 gap-3">
          <Input
            id="profile-first-name"
            aria-label="First name"
            placeholder="First name"
            autoComplete="given-name"
            className={FIELD}
            {...fieldA11y("profile-first-name", nameError)}
            {...register("first_name")}
          />
          <Input
            aria-label="Last name"
            placeholder="Last name"
            autoComplete="family-name"
            className={FIELD}
            aria-invalid={errors.last_name ? true : undefined}
            {...register("last_name")}
          />
        </div>
      </FormField>

      <FormField id="profile-display-name" label="Display Name" error={errors.display_name?.message}>
        <Input
          id="profile-display-name"
          placeholder={user.first_name}
          autoComplete="nickname"
          className={FIELD}
          aria-invalid={errors.display_name ? true : undefined}
          aria-describedby={errors.display_name ? "profile-display-name-error" : "profile-display-name-hint"}
          {...register("display_name")}
        />
        <p id="profile-display-name-hint" className="text-sm text-muted-foreground">
          We'll address you by this name in the app
        </p>
      </FormField>

      <FormField id="profile-birthday" label="Birthday" error={errors.birthday?.message}>
        {/* The browser's own date picker, with its calendar button on the right like Monarch's */}
        <Input
          id="profile-birthday"
          type="date"
          min="1900-01-01"
          max={todayInputValue()}
          className={FIELD}
          {...fieldA11y("profile-birthday", errors.birthday?.message)}
          {...register("birthday")}
        />
      </FormField>

      <FormField id="profile-timezone" label="Timezone" error={errors.timezone?.message}>
        <NativeSelect id="profile-timezone" className={FIELD} {...register("timezone")}>
          {timezoneChoices(user.timezone ?? BROWSER_TIMEZONE).map((zone) => (
            <option key={zone} value={zone}>
              {zone}
            </option>
          ))}
        </NativeSelect>
      </FormField>

      <Button type="submit" size="lg" className="h-10 w-full" disabled={!isDirty || updateProfile.isPending}>
        {updateProfile.isPending ? "Updating profile…" : "Update Profile"}
      </Button>
    </form>
  )
}
