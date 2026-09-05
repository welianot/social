import { createClient } from "./supabase";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

async function getToken(): Promise<string | null> {
  const supabase = createClient();
  const { data } = await supabase.auth.getSession();
  return data.session?.access_token ?? null;
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getToken();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Request failed");
  }
  return res.json();
}

// ── Users ──────────────────────────────────────────
export const api = {
  getMe: () => request<Profile>("/users/me"),
  updateMe: (data: Partial<Profile>) =>
    request<Profile>("/users/me", { method: "PATCH", body: JSON.stringify(data) }),
  getProfile: (username: string) => request<Profile>(`/users/${username}`),
  follow: (username: string) =>
    request(`/users/${username}/follow`, { method: "POST" }),
  unfollow: (username: string) =>
    request(`/users/${username}/follow`, { method: "DELETE" }),

  // ── Feed ─────────────────────────────────────────
  getHomeFeed: (page = 1) => request<FeedResponse>(`/feed/home?page=${page}`),
  getTrending: (page = 1) => request<FeedResponse>(`/feed/trending?page=${page}`),
  getUserFeed: (username: string, page = 1) =>
    request<FeedResponse>(`/feed/user/${username}?page=${page}`),

  // ── Posts ────────────────────────────────────────
  createPost: (formData: FormData) =>
    request<Post>("/posts", { method: "POST", body: formData }),
  likePost: (id: string) => request(`/posts/${id}/like`, { method: "POST" }),
  unlikePost: (id: string) => request(`/posts/${id}/like`, { method: "DELETE" }),
  getComments: (id: string) => request<Comment[]>(`/posts/${id}/comments`),
  addComment: (id: string, body: string) =>
    request<Comment>(`/posts/${id}/comments`, {
      method: "POST",
      body: JSON.stringify({ body }),
    }),

  // ── Explore ──────────────────────────────────────
  exploreUsers: (params: { country?: string; interest?: string; q?: string; page?: number }) => {
    const qs = new URLSearchParams();
    if (params.country) qs.set("country", params.country);
    if (params.interest) qs.set("interest", params.interest);
    if (params.q) qs.set("q", params.q);
    if (params.page) qs.set("page", String(params.page));
    return request<{ items: Profile[]; total: number }>(`/explore/users?${qs}`);
  },
  getCountries: () => request<{ code: string; count: number }[]>("/explore/countries"),

  // ── Messages ─────────────────────────────────────
  getConversations: () => request<Conversation[]>("/messages/conversations"),
  createConversation: (participantId: string) =>
    request<{ id: string }>("/messages/conversations", {
      method: "POST",
      body: JSON.stringify({ participant_id: participantId }),
    }),
  getMessages: (conversationId: string, page = 1) =>
    request<{ items: Message[] }>(`/messages/conversations/${conversationId}?page=${page}`),
  sendMessage: (conversationId: string, body: string) =>
    request<Message>(`/messages/conversations/${conversationId}`, {
      method: "POST",
      body: JSON.stringify({ body }),
    }),
};

// ── Types ──────────────────────────────────────────
export interface Profile {
  id: string;
  username: string;
  display_name: string | null;
  bio: string | null;
  avatar_url: string | null;
  country: string | null;
  language: string | null;
  interests: string[];
  is_creator: boolean;
  is_verified: boolean;
  follower_count: number;
  following_count: number;
  post_count: number;
}

export interface Post {
  id: string;
  creator_id: string;
  content_type: string;
  caption: string | null;
  like_count: number;
  comment_count: number;
  created_at: string;
  media: { url: string; media_type: string }[];
  creator: Pick<Profile, "id" | "username" | "display_name" | "avatar_url" | "is_verified"> | null;
  liked_by_me: boolean;
}

export interface FeedResponse {
  items: Post[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface Comment {
  id: string;
  body: string;
  created_at: string;
  user: Pick<Profile, "id" | "username" | "display_name" | "avatar_url"> | null;
}

export interface Conversation {
  id: string;
  participants: Pick<Profile, "id" | "username" | "display_name" | "avatar_url">[];
  last_message: Message | null;
}

export interface Message {
  id: string;
  sender_id: string;
  body: string;
  created_at: string;
  read_at: string | null;
}
