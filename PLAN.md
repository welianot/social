# Meets — Platform Plan

> **Where the world meets.** 🌍  
> One word. Social · Discovery · Marketplace · Courses · Creator monetization.

---

## 1. Brand → Product Mapping

| Brand line | Product surface |
|---|---|
| Meets people | Profiles, follow graph, DMs |
| Meets cultures | Explore by country + language |
| Meets buyers & sellers | Marketplace + affiliate links |
| Meets learners & teachers | Courses (Phase 4) |
| Meets fans & creators | Subscriptions, tips, exclusive content |

---

## 2. Tech Stack (locked)

| Layer | Choice | Why |
|---|---|---|
| Frontend | **Next.js 14 App Router** | SSR for SEO profiles, route groups for adult section |
| UI | **Tailwind + shadcn/ui** | Fast, accessible, composable |
| Backend | **FastAPI** | Async, typed, great for media/affiliate/payment services |
| DB + Auth | **Supabase (PostgreSQL)** | Auth, RLS, Realtime in one |
| Realtime chat | **Supabase Realtime** | DMs without running a separate WebSocket server |
| Media | **Supabase Storage** (Phase 1) → R2 later if cost grows | Simple start |
| Cache / rate limit | **Redis** | Feed cache, rate limits, session blacklist |
| Payments | **Stripe** (intl) + **Razorpay** (India) | Phase 2 |
| Adult payments | **CCBill / Segpay** (Phase 2+, separate) | Stripe blocks adult |

### Frontend note: Google Stitch

You mentioned using **Stitch** for frontend UI generation. Recommended split:

- **Stitch** → page layouts, component shells, visual polish (feed cards, profile, explore grid)
- **This repo** → route structure, Supabase client, API client, auth guards, data fetching hooks

Stitch exports React/Tailwind — drop components into `frontend/components/` and wire to existing `lib/supabase.ts` + `lib/api.ts`.

---

## 3. Repository Layout

```
meets/
├── PLAN.md                     ← this file
├── README.md                   ← setup guide
├── frontend/                   ← Next.js 14
│   ├── app/
│   │   ├── (auth)/             ← login, register
│   │   ├── (main)/             ← feed, explore, messages, marketplace, profile
│   │   └── (adult)/            ← age-gated, web-only (Phase 2+)
│   ├── components/
│   └── lib/
├── backend/                    ← FastAPI
│   ├── main.py
│   ├── core/
│   ├── middleware/
│   ├── routers/
│   ├── schemas/
│   └── services/
└── supabase/
    └── schema.sql
```

---

## 4. Phased Roadmap

### Phase 1 — Core Social (MVP) ← **BUILD NOW**

| Feature | Backend | DB | Frontend |
|---|---|---|---|
| Sign up / profile (location, language) | `auth`, `users` | `profiles` | register, profile edit |
| Post feed (photo, video, caption) | `posts`, `media` | `posts`, `post_media` | feed, create post |
| Discover by country/interest | `explore` | indexes on `country`, `interests` | explore page |
| Follow / like / comment | `users`, `posts` | `follows`, `likes`, `comments` | actions on post card |
| DM chat | `messages` | `conversations`, `messages` | messages page + Realtime |

**Phase 1 exit criteria:** Two users can register, post, follow, like, comment, and DM in realtime.

### Phase 2 — Creator Monetization

- Creator profiles + subscription tiers
- Exclusive (subscriber-only) posts
- Tips / donations
- Stripe Connect + Razorpay payouts
- Adult section: separate subdomain, age verification (Veriff/Onfido), CCBill

### Phase 3 — Marketplace

- Physical/digital product listings
- Chat-to-buy flow
- Order states: pending → paid → shipped → complete
- Affiliate auto-fetch (Amazon/Flipkart)

### Phase 4 — Knowledge & News

- Course upload + enrollment + progress
- News/sports feeds via API (NewsAPI, etc.)
- Trade signals content type

---

## 5. Content Types (full vision, phased)

| Type | Phase | Storage | Notes |
|---|---|---|---|
| Photo post | 1 | Supabase Storage | |
| Video (short/long) | 1 | Supabase Storage | transcode later (Mux/Cloudflare Stream) |
| Audio (podcast/music) | 2 | Supabase Storage | |
| News/article | 4 | DB text + optional image | |
| Adult content | 2+ | Separate bucket + CDN | age-gated, web-only |
| Product listing | 3 | DB + affiliate URL | auto-fetch title/image/price |
| Course | 4 | DB + video lessons | |
| Trade signals | 4 | DB structured fields | |

Post model uses `content_type` enum — one table, polymorphic metadata JSONB.

---

## 6. Database Design (summary)

Core tables (Phase 1):

```
profiles          ← extends auth.users (username, bio, country, language, avatar)
posts             ← content_type, caption, is_adult, visibility, creator_id
post_media        ← url, media_type, order
follows           ← follower_id, following_id
likes             ← user_id, post_id
comments          ← user_id, post_id, body, parent_id (threading)
conversations     ← participant pair or group
messages          ← conversation_id, sender_id, body, read_at
notifications     ← user_id, type, payload, read_at
```

Phase 2+ tables (schema included, unused until needed):

```
creator_tiers, subscriptions, tips, payouts
products, orders, order_items
courses, lessons, enrollments
affiliate_links
```

All tables have **RLS enabled**. FastAPI uses service role for admin; user JWT for client calls.

---

## 7. API Design

Base: `http://localhost:8000/api/v1`

| Router | Key endpoints |
|---|---|
| `/auth` | POST register, login, refresh, logout |
| `/users` | GET/PATCH profile, POST follow/unfollow, GET followers |
| `/posts` | CRUD, like, comment, upload media |
| `/feed` | GET home feed, GET user posts, GET trending |
| `/explore` | GET by country, interest, search users |
| `/messages` | conversations CRUD, send message |
| `/products` | Phase 3 |
| `/payments` | Phase 2 |
| `/creators` | Phase 2 |
| `/admin` | ban, verify, stats |

Auth: Supabase JWT in `Authorization: Bearer <token>`. FastAPI validates via Supabase JWKS.

---

## 8. Key Platform Decisions

### 8.1 Adult content
- **Not in Phase 1.** Schema has `is_adult` flag + separate route group ready.
- Requires: age verification provider, separate storage bucket, CCBill/Segpay, legal review per country.
- **Web only** — no App Store distribution for adult section.

### 8.2 Amazon/Flipkart affiliate
- Phase 3: paste URL → backend fetches OG meta / product API → stores title, image, price.
- Inject platform affiliate tag server-side (never expose keys to client).
- Commission: platform cut configurable in `core/config.py`.

### 8.3 Monetization (Meets revenue)
- 10% platform fee on creator subscriptions (configurable)
- 5% on marketplace sales
- Promoted posts / ads — Phase 5
- Premium accounts — Phase 5

### 8.4 Media strategy
- Phase 1: direct upload to Supabase Storage (max 50MB video, 10MB image)
- Phase 2+: Mux or Cloudflare Stream for transcoding + HLS

### 8.5 Auth flow
- Supabase Auth handles signup/login on frontend
- Frontend sends JWT to FastAPI for business logic
- FastAPI never stores passwords — Supabase owns auth

---

## 9. Security Checklist

- [x] RLS on all Supabase tables
- [x] Rate limiting via Redis (100 req/min per IP default)
- [x] JWT validation on all protected routes
- [ ] Content moderation queue (Phase 2)
- [ ] Adult age verification (Phase 2+)
- [ ] CSRF on cookie-based flows (if added later)

---

## 10. Implementation Order (this session)

1. ✅ `PLAN.md` — this document
2. ✅ `supabase/schema.sql` — full schema, Phase 1 active
3. ✅ `backend/` — FastAPI skeleton, Phase 1 routers wired
4. ✅ `frontend/` — Next.js scaffold, route groups, lib clients
5. ✅ `.env.example` files + README

**Next session after Stitch UI:**
- Wire Stitch components to API hooks
- Supabase project creation + run schema
- End-to-end test: register → post → feed → DM

---

## 11. Environment Variables

### Backend (`backend/.env`)
```
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
SUPABASE_JWT_SECRET=
REDIS_URL=redis://localhost:6379
STRIPE_SECRET_KEY=          # Phase 2
RAZORPAY_KEY_ID=            # Phase 2
PLATFORM_FEE_SUBSCRIPTION=0.10
PLATFORM_FEE_MARKETPLACE=0.05
CORS_ORIGINS=http://localhost:3000
```

### Frontend (`frontend/.env.local`)
```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 12. What Stitch Should Generate

If using Google Stitch, prompt it for these screens (wire to our API contracts):

1. **Auth** — login/register with country + language picker
2. **Feed** — infinite scroll post cards (photo/video, like/comment actions)
3. **Create post** — media upload + caption
4. **Explore** — country filter chips + user grid
5. **Profile** — avatar, bio, posts grid, follow button
6. **Messages** — conversation list + chat thread
7. **Navbar** — feed / explore / create / messages / profile

Export as React + Tailwind. Place in `frontend/components/`. Hook up via:
- `lib/supabase.ts` for auth
- `lib/api.ts` for FastAPI calls
