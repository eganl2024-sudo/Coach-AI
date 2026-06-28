import { redirect } from 'next/navigation'
import { getCurrentParent } from '@/lib/session'

export default async function RootPage() {
  const parent = await getCurrentParent()
  redirect(parent ? '/home' : '/login')
}
