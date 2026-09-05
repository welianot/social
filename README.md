# Meets

> Where the world meets. 🌍

## Setup commands

Run these in order from the project root (`social/`).

### 1. Supabase

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** → paste and run `supabase/schema.sql`
3. Go to **Storage** → create buckets: `avatars`, `posts` (public), `adult` (private)
4. Copy your project URL, anon key, service role key, and JWT secret

### 2. Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edit .env with your Supabase credentials
uvicorn main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 3. Frontend

```powershell
cd frontend
npm install
copy .env.local.example .env.local
# Edit .env.local with your Supabase URL + anon key
npm run dev
```

App: http://localhost:3000

### 4. Redis (optional, for rate limiting)

```powershell
# With Docker:
docker run -d -p 6379:6379 redis:7-alpine

# Or install Redis for Windows and set REDIS_URL in backend/.env
```

If Redis is not running, rate limiting is skipped gracefully.

---

## Project structure

```
meets/
├── PLAN.md              ← full roadmap + decisions
├── supabase/schema.sql  ← run in Supabase SQL Editor
├── backend/             ← FastAPI (port 8000)
└── frontend/            ← Next.js 14 (port 3000)
```

## Using Google Stitch for UI

Stitch generates the visual components. Drop them into `frontend/components/` and wire to:

- `lib/supabase.ts` — auth
- `lib/api.ts` — all FastAPI calls

Screens to generate in Stitch: login, register, feed, explore, profile, messages, create post.

## Phases

| Phase | Status |
|---|---|
| 1 — Core Social (MVP) | ✅ scaffolded |
| 2 — Creator monetization | schema ready, endpoints stubbed |
| 3 — Marketplace + affiliate | affiliate preview ready |
| 4 — Courses + news | schema ready |

See `PLAN.md` for full details.
