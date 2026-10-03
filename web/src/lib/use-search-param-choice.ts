import { useSearchParams } from "react-router"

/**
 * One of a fixed set of choices, kept in the URL (so links and reloads keep it).
 * The default choice leaves the URL clean; an unknown value in the URL reads as the default.
 */
export function useSearchParamChoice<Choice extends string>(
  param: string,
  isChoice: (value: string | null) => value is Choice,
  fallback: Choice,
): [Choice, (next: Choice) => void] {
  const [params, setParams] = useSearchParams()
  const value = params.get(param)
  const choice = isChoice(value) ? value : fallback

  function setChoice(next: Choice) {
    setParams((current) => {
      const updated = new URLSearchParams(current)
      if (next === fallback) updated.delete(param)
      else updated.set(param, next)
      return updated
    })
  }

  return [choice, setChoice]
}
