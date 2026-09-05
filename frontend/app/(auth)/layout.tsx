export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-violet-50 via-white to-indigo-50 px-4">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-primary">Meets 🌍</h1>
        <p className="text-muted-foreground text-sm mt-1">Where the world meets</p>
      </div>
      <div className="w-full max-w-sm">{children}</div>
    </div>
  );
}
