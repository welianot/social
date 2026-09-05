"use client";

import Link from "next/link";
import { Post } from "@/lib/api";
import { api } from "@/lib/api";
import { useState } from "react";

export function PostCard({ post }: { post: Post }) {
  const [liked, setLiked] = useState(post.liked_by_me);
  const [likeCount, setLikeCount] = useState(post.like_count);

  async function toggleLike() {
    if (liked) {
      await api.unlikePost(post.id);
      setLikeCount((c) => c - 1);
    } else {
      await api.likePost(post.id);
      setLikeCount((c) => c + 1);
    }
    setLiked(!liked);
  }

  return (
    <article className="border rounded-xl overflow-hidden">
      <div className="flex items-center gap-2 p-3">
        <Link href={`/profile/${post.creator?.username}`} className="font-medium text-sm hover:underline">
          {post.creator?.display_name ?? post.creator?.username}
        </Link>
      </div>
      {post.media[0] && (
        <div className="aspect-square bg-muted">
          {post.media[0].media_type === "video" ? (
            <video src={post.media[0].url} controls className="w-full h-full object-cover" />
          ) : (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={post.media[0].url} alt="" className="w-full h-full object-cover" />
          )}
        </div>
      )}
      <div className="p-3 space-y-2">
        <div className="flex gap-4 text-sm">
          <button onClick={toggleLike} className={liked ? "text-red-500" : ""}>
            {liked ? "♥" : "♡"} {likeCount}
          </button>
          <span className="text-muted-foreground">{post.comment_count} comments</span>
        </div>
        {post.caption && <p className="text-sm">{post.caption}</p>}
      </div>
    </article>
  );
}
