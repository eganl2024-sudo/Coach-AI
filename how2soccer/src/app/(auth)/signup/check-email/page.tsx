import Link from 'next/link'

export default function CheckEmailPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white flex flex-col items-center justify-center px-6">
      <div className="w-full max-w-sm text-center space-y-4">
        <div className="text-6xl">📬</div>
        <h1 className="text-2xl font-black text-gray-900">Check your email</h1>
        <p className="text-gray-500">
          We sent a confirmation link to your email address. Click it to activate your account and add your first player.
        </p>
        <p className="text-sm text-gray-400">The link expires in 24 hours.</p>
        <Link href="/login" className="block text-sm text-green-600 font-semibold hover:underline mt-4">
          Back to login
        </Link>
      </div>
    </div>
  )
}
