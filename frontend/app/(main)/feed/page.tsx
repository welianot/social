"use client";

import { useEffect, useState } from "react";
import { api, Post } from "@/lib/api";
import { PostCard } from "@/components/post/post-card";

export default function FeedPage() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);

  useEffect(() => {
    api.getHomeFeed(page).then((res) => {
      setPosts((prev) => (page === 1 ? res.items : [...prev, ...res.items]));
      setHasMore(res.has_more);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [page]);

  if (loading) return <p className="text-muted-foreground text-sm">Loading feed…</p>;

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold">Feed</h1>
      {posts.length === 0 && (
        <p className="text-muted-foreground text-sm">
          Follow people to see their posts here.
        </p>
      )}
      {posts.map((post) => (
        <PostCard key={post.id} post={post} />
      ))}
      {hasMore && (
        <button
          onClick={() => setPage((p) => p + 1)}
          className="w-full text-sm text-primary py-2"
        >
          Load more
        </button>
      )}
    </div>
  );
}
