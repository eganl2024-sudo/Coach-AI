export function getLocalDate(timezone = 'America/New_York'): string {
  return new Date().toLocaleDateString('en-CA', { timeZone: timezone })
}

export function getLocalYesterday(timezone = 'America/New_York'): string {
  const d = new Date()
  d.setDate(d.getDate() - 1)
  return d.toLocaleDateString('en-CA', { timeZone: timezone })
}
