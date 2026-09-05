"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { createClient } from "@/lib/supabase";

const COUNTRIES = [
  { code: "IN", name: "🇮🇳 India" },
  { code: "US", name: "🇺🇸 United States" },
  { code: "GB", name: "🇬🇧 United Kingdom" },
  { code: "DE", name: "🇩🇪 Germany" },
  { code: "FR", name: "🇫🇷 France" },
  { code: "JP", name: "🇯🇵 Japan" },
  { code: "BR", name: "🇧🇷 Brazil" },
  { code: "AU", name: "🇦🇺 Australia" },
  { code: "NG", name: "🇳🇬 Nigeria" },
  { code: "ZA", name: "🇿🇦 South Africa" },
];

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    email: "",
    password: "",
    username: "",
    country: "IN",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function set(key: string, value: string) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    const supabase = createClient();

    const { error } = await supabase.auth.signUp({
      email: form.email,
      password: form.password,
      options: {
        data: {
          username: form.username,
          display_name: form.username,
        },
      },
    });

    if (error) {
      setError(error.message);
      setLoading(false);
      return;
    }

    router.push("/feed");
    router.refresh();
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-border p-8">
      <h2 className="text-xl font-semibold mb-1">Create account</h2>
      <p className="text-muted-foreground text-sm mb-6">Join the Meets community</p>

      <form onSubmit={handleRegister} className="space-y-4">
        <div>
          <label className="text-sm font-medium block mb-1.5">Username</label>
          <input
            type="text"
            placeholder="yourname"
            value={form.username}
            onChange={(e) => set("username", e.target.value.toLowerCase().replace(/\s/g, ""))}
            className="w-full border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition"
            required
          />
        </div>
        <div>
          <label className="text-sm font-medium block mb-1.5">Email</label>
          <input
            type="email"
            placeholder="you@example.com"
            value={form.email}
            onChange={(e) => set("email", e.target.value)}
            className="w-full border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition"
            required
          />
        </div>
        <div>
          <label className="text-sm font-medium block mb-1.5">Password</label>
          <input
            type="password"
            placeholder="Min 6 characters"
            value={form.password}
            onChange={(e) => set("password", e.target.value)}
            className="w-full border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition"
            minLength={6}
            required
          />
        </div>
        <div>
          <label className="text-sm font-medium block mb-1.5">Country</label>
          <select
            value={form.country}
            onChange={(e) => set("country", e.target.value)}
            className="w-full border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition"
          >
            {COUNTRIES.map((c) => (
              <option key={c.code} value={c.code}>{c.name}</option>
            ))}
          </select>
        </div>

        {error && (
          <p className="text-red-500 text-sm bg-red-50 border border-red-200 rounded-lg px-3 py-2">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-primary text-primary-foreground rounded-lg py-2.5 text-sm font-medium hover:opacity-90 transition disabled:opacity-50"
        >
          {loading ? "Creating account…" : "Create account"}
        </button>
      </form>

      <p className="text-sm text-muted-foreground mt-5 text-center">
        Already have an account?{" "}
        <Link href="/login" className="text-primary font-medium hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  );
}
