"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, Profile, Post } from "@/lib/api";
import { PostCard } from "@/components/post/post-card";

export default function ProfilePage() {
  const { username } = useParams<{ username: string }>();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);

  useEffect(() => {
    api.getProfile(username).then(setProfile);
    api.getUserFeed(username).then((res) => setPosts(res.items));
  }, [username]);

  if (!profile) return <p className="text-muted-foreground text-sm">Loading…</p>;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <div className="w-16 h-16 rounded-full bg-muted overflow-hidden">
          {profile.avatar_url && (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={profile.avatar_url} alt="" className="w-full h-full object-cover" />
          )}
        </div>
        <div>
          <h1 className="font-semibold">{profile.display_name ?? profile.username}</h1>
          <p className="text-sm text-muted-foreground">@{profile.username}</p>
          {profile.bio && <p className="text-sm mt-1">{profile.bio}</p>}
          <div className="flex gap-4 text-xs text-muted-foreground mt-2">
            <span>{profile.follower_count} followers</span>
            <span>{profile.following_count} following</span>
            <span>{profile.post_count} posts</span>
          </div>
        </div>
      </div>
      <div className="space-y-4">
        {posts.map((post) => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>
    </div>
  );
}
