"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, Profile } from "@/lib/api";

export default function ExplorePage() {
  const [users, setUsers] = useState<Profile[]>([]);
  const [countries, setCountries] = useState<{ code: string; count: number }[]>([]);
  const [country, setCountry] = useState("");
  const [q, setQ] = useState("");

  useEffect(() => {
    api.getCountries().then(setCountries);
  }, []);

  useEffect(() => {
    api.exploreUsers({ country: country || undefined, q: q || undefined }).then(
      (res) => setUsers(res.items)
    );
  }, [country, q]);

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold">Explore</h1>
      <input
        type="search"
        placeholder="Search people…"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        className="w-full border rounded-lg px-3 py-2 text-sm"
      />
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => setCountry("")}
          className={`text-xs px-3 py-1 rounded-full border ${!country ? "bg-primary text-white border-primary" : ""}`}
        >
          All
        </button>
        {countries.map((c) => (
          <button
            key={c.code}
            onClick={() => setCountry(c.code)}
            className={`text-xs px-3 py-1 rounded-full border ${country === c.code ? "bg-primary text-white border-primary" : ""}`}
          >
            {c.code} ({c.count})
          </button>
        ))}
      </div>
      <div className="grid grid-cols-2 gap-3">
        {users.map((u) => (
          <Link
            key={u.id}
            href={`/profile/${u.username}`}
            className="border rounded-xl p-4 hover:bg-muted/50 transition"
          >
            <div className="w-10 h-10 rounded-full bg-muted mb-2 overflow-hidden">
              {u.avatar_url && (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={u.avatar_url} alt="" className="w-full h-full object-cover" />
              )}
            </div>
            <p className="font-medium text-sm">{u.display_name ?? u.username}</p>
            <p className="text-xs text-muted-foreground">@{u.username}</p>
            {u.country && (
              <p className="text-xs text-muted-foreground mt-1">{u.country}</p>
            )}
          </Link>
        ))}
      </div>
    </div>
  );
}
