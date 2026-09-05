"use client";

import Link from "next/link";
import { Post, api } from "@/lib/api";
import { useState } from "react";

function timeAgo(date: string) {
  const diff = Date.now() - new Date(date).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h`;
  return `${Math.floor(hrs / 24)}d`;
}

export function PostCard({ post }: { post: Post }) {
  const [liked, setLiked] = useState(post.liked_by_me);
  const [likeCount, setLikeCount] = useState(post.like_count);
  const [busy, setBusy] = useState(false);

  async function toggleLike() {
    if (busy) return;
    setBusy(true);
    try {
      if (liked) {
        await api.unlikePost(post.id);
        setLikeCount((c) => Math.max(0, c - 1));
      } else {
        await api.likePost(post.id);
        setLikeCount((c) => c + 1);
      }
      setLiked(!liked);
    } finally {
      setBusy(false);
    }
  }

  const creator = post.creator;

  return (
    <article className="bg-white border border-border rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3">
        <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center text-sm font-bold text-primary flex-shrink-0 overflow-hidden">
          {creator?.avatar_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={creator.avatar_url} alt="" className="w-full h-full object-cover" />
          ) : (
            (creator?.display_name ?? creator?.username ?? "?")[0].toUpperCase()
          )}
        </div>
        <div className="flex-1 min-w-0">
          <Link
            href={`/profile/${creator?.username}`}
            className="font-semibold text-sm hover:underline truncate block"
          >
            {creator?.display_name ?? creator?.username ?? "Unknown"}
            {creator?.is_verified && <span className="ml-1 text-primary">✓</span>}
          </Link>
          <p className="text-xs text-muted-foreground">{timeAgo(post.created_at)}</p>
        </div>
      </div>

      {/* Media */}
      {post.media[0] && (
        <div className="bg-muted w-full aspect-square">
          {post.media[0].media_type === "video" ? (
            <video
              src={post.media[0].url}
              controls
              className="w-full h-full object-cover"
            />
          ) : (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={post.media[0].url}
              alt={post.caption ?? ""}
              className="w-full h-full object-cover"
            />
          )}
        </div>
      )}

      {/* Actions + caption */}
      <div className="px-4 py-3 space-y-2">
        <div className="flex items-center gap-4">
          <button
            onClick={toggleLike}
            disabled={busy}
            className={`flex items-center gap-1.5 text-sm font-medium transition ${
              liked ? "text-red-500" : "text-muted-foreground hover:text-red-400"
            }`}
          >
            <span className="text-base">{liked ? "♥" : "♡"}</span>
            <span>{likeCount}</span>
          </button>
          <span className="flex items-center gap-1.5 text-sm text-muted-foreground">
            <span className="text-base">💬</span>
            <span>{post.comment_count}</span>
          </span>
        </div>
        {post.caption && (
          <p className="text-sm leading-relaxed">
            <span className="font-semibold mr-1">
              {creator?.username}
            </span>
            {post.caption}
          </p>
        )}
      </div>
    </article>
  );
}
