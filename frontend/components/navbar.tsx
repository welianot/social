import Link from "next/link";

const NAV = [
  { href: "/feed", label: "Feed" },
  { href: "/explore", label: "Explore" },
  { href: "/messages", label: "Messages" },
  { href: "/marketplace", label: "Shop" },
];

export function Navbar() {
  return (
    <header className="border-b sticky top-0 bg-white/80 backdrop-blur z-10">
      <div className="max-w-2xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link href="/feed" className="font-bold text-primary">
          Meets 🌍
        </Link>
        <nav className="flex gap-4">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="text-sm text-muted-foreground hover:text-foreground"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
