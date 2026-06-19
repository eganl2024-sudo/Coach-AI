// Standalone layout for admin login — bypasses parent admin layout
// so the login page renders without triggering the auth redirect loop
export default function AdminLoginLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
