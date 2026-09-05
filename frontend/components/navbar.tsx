"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase";

const NAV = [
  { href: "/feed",        label: "Feed",     icon: "🏠" },
  { href: "/explore",     label: "Explore",  icon: "🔍" },
  { href: "/messages",    label: "Messages", icon: "💬" },
  { href: "/marketplace", label: "Shop",     icon: "🛍️" },
];

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();

  async function handleLogout() {
    const supabase = createClient();
    await supabase.auth.signOut();
    router.push("/login");
    router.refresh();
  }

  return (
    <header className="border-b sticky top-0 bg-white/90 backdrop-blur z-10">
      <div className="max-w-2xl mx-auto px-4 h-14 flex items-center justify-between">
        {/* Logo */}
        <Link href="/feed" className="font-bold text-primary text-lg tracking-tight">
          Meets 🌍
        </Link>

        {/* Nav links */}
        <nav className="flex items-center gap-1">
          {NAV.map((item) => {
            const active = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`px-3 py-1.5 rounded-lg text-sm transition font-medium ${
                  active
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted"
                }`}
              >
                <span className="hidden sm:inline">{item.label}</span>
                <span className="sm:hidden">{item.icon}</span>
              </Link>
            );
          })}

          {/* Profile + logout */}
          <Link
            href="/profile/me"
            className="px-3 py-1.5 rounded-lg text-sm text-muted-foreground hover:text-foreground hover:bg-muted transition font-medium"
          >
            <span className="hidden sm:inline">Profile</span>
            <span className="sm:hidden">👤</span>
          </Link>
          <button
            onClick={handleLogout}
            className="px-3 py-1.5 rounded-lg text-sm text-muted-foreground hover:text-red-500 hover:bg-red-50 transition font-medium"
          >
            <span className="hidden sm:inline">Logout</span>
            <span className="sm:hidden">↩</span>
          </button>
        </nav>
      </div>
    </header>
  );
}
