-- Meets Platform — Full Database Schema
-- Run in Supabase SQL Editor after creating project

-- ============================================================
-- EXTENSIONS
-- ============================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- for text search

-- ============================================================
-- ENUMS
-- ============================================================
CREATE TYPE content_type AS ENUM (
  'photo', 'video', 'audio', 'article',
  'product', 'course', 'trade_signal', 'adult'
);

CREATE TYPE media_type AS ENUM ('image', 'video', 'audio');

CREATE TYPE post_visibility AS ENUM ('public', 'followers', 'subscribers');

CREATE TYPE notification_type AS ENUM (
  'follow', 'like', 'comment', 'message',
  'subscription', 'tip', 'order', 'system'
);

CREATE TYPE order_status AS ENUM (
  'pending', 'paid', 'shipped', 'completed', 'cancelled', 'refunded'
);

-- ============================================================
-- PROFILES (extends auth.users)
-- ============================================================
CREATE TABLE profiles (
  id            UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username      TEXT UNIQUE NOT NULL,
  display_name  TEXT,
  bio           TEXT,
  avatar_url    TEXT,
  country       TEXT,           -- ISO 3166-1 alpha-2 e.g. 'IN', 'US'
  language      TEXT DEFAULT 'en', -- ISO 639-1
  interests     TEXT[] DEFAULT '{}',
  is_creator    BOOLEAN DEFAULT FALSE,
  is_verified   BOOLEAN DEFAULT FALSE,
  is_adult_creator BOOLEAN DEFAULT FALSE,
  follower_count  INT DEFAULT 0,
  following_count INT DEFAULT 0,
  post_count      INT DEFAULT 0,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_profiles_username ON profiles(username);
CREATE INDEX idx_profiles_country ON profiles(country);
CREATE INDEX idx_profiles_interests ON profiles USING GIN(interests);

-- ============================================================
-- POSTS
-- ============================================================
CREATE TABLE posts (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  creator_id    UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  content_type  content_type NOT NULL DEFAULT 'photo',
  caption       TEXT,
  visibility    post_visibility DEFAULT 'public',
  is_adult      BOOLEAN DEFAULT FALSE,
  metadata      JSONB DEFAULT '{}',  -- polymorphic: product_url, course_id, etc.
  like_count    INT DEFAULT 0,
  comment_count INT DEFAULT 0,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_posts_creator ON posts(creator_id, created_at DESC);
CREATE INDEX idx_posts_feed ON posts(created_at DESC) WHERE is_adult = FALSE;
CREATE INDEX idx_posts_adult ON posts(created_at DESC) WHERE is_adult = TRUE;
CREATE INDEX idx_posts_content_type ON posts(content_type);

-- ============================================================
-- POST MEDIA
-- ============================================================
CREATE TABLE post_media (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  post_id     UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
  url         TEXT NOT NULL,
  media_type  media_type NOT NULL,
  sort_order  INT DEFAULT 0,
  width       INT,
  height      INT,
  duration_s  INT,  -- for video/audio
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_post_media_post ON post_media(post_id, sort_order);

-- ============================================================
-- SOCIAL GRAPH
-- ============================================================
CREATE TABLE follows (
  follower_id   UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  following_id  UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (follower_id, following_id),
  CHECK (follower_id != following_id)
);

CREATE INDEX idx_follows_following ON follows(following_id);

CREATE TABLE likes (
  user_id     UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  post_id     UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (user_id, post_id)
);

CREATE INDEX idx_likes_post ON likes(post_id);

CREATE TABLE comments (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  post_id     UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
  user_id     UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  parent_id   UUID REFERENCES comments(id) ON DELETE CASCADE,
  body        TEXT NOT NULL,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_comments_post ON comments(post_id, created_at);

-- ============================================================
-- MESSAGING
-- ============================================================
CREATE TABLE conversations (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE conversation_participants (
  conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  user_id         UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  joined_at       TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (conversation_id, user_id)
);

CREATE TABLE messages (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  sender_id       UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  body            TEXT NOT NULL,
  read_at         TIMESTAMPTZ,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at DESC);

-- ============================================================
-- NOTIFICATIONS
-- ============================================================
CREATE TABLE notifications (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id     UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  type        notification_type NOT NULL,
  payload     JSONB DEFAULT '{}',
  read_at     TIMESTAMPTZ,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id, created_at DESC);

-- ============================================================
-- PHASE 2: CREATOR MONETIZATION
-- ============================================================
CREATE TABLE creator_tiers (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  creator_id    UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  name          TEXT NOT NULL,
  price_cents   INT NOT NULL,
  currency      TEXT DEFAULT 'USD',
  description   TEXT,
  stripe_price_id TEXT,
  razorpay_plan_id TEXT,
  is_active     BOOLEAN DEFAULT TRUE,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE subscriptions (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  subscriber_id   UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  creator_id      UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  tier_id         UUID NOT NULL REFERENCES creator_tiers(id),
  status          TEXT DEFAULT 'active',  -- active, cancelled, expired
  stripe_sub_id   TEXT,
  razorpay_sub_id TEXT,
  current_period_end TIMESTAMPTZ,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_subscriber ON subscriptions(subscriber_id);
CREATE INDEX idx_subscriptions_creator ON subscriptions(creator_id);

CREATE TABLE tips (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  sender_id     UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  creator_id    UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  amount_cents  INT NOT NULL,
  currency      TEXT DEFAULT 'USD',
  message       TEXT,
  stripe_payment_id TEXT,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- PHASE 3: MARKETPLACE
-- ============================================================
CREATE TABLE products (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  seller_id     UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  title         TEXT NOT NULL,
  description   TEXT,
  price_cents   INT,
  currency      TEXT DEFAULT 'USD',
  image_url     TEXT,
  is_digital    BOOLEAN DEFAULT FALSE,
  is_affiliate  BOOLEAN DEFAULT FALSE,
  affiliate_url TEXT,
  affiliate_source TEXT,  -- 'amazon', 'flipkart', etc.
  affiliate_meta  JSONB DEFAULT '{}',
  is_active     BOOLEAN DEFAULT TRUE,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_products_seller ON products(seller_id);

CREATE TABLE orders (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  buyer_id      UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  seller_id     UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  status        order_status DEFAULT 'pending',
  total_cents   INT NOT NULL,
  currency      TEXT DEFAULT 'USD',
  stripe_payment_id TEXT,
  razorpay_order_id TEXT,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE order_items (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  order_id    UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
  product_id  UUID NOT NULL REFERENCES products(id),
  quantity    INT DEFAULT 1,
  price_cents INT NOT NULL
);

-- ============================================================
-- PHASE 4: COURSES
-- ============================================================
CREATE TABLE courses (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  creator_id    UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  title         TEXT NOT NULL,
  description   TEXT,
  price_cents   INT DEFAULT 0,
  currency      TEXT DEFAULT 'USD',
  thumbnail_url TEXT,
  is_published  BOOLEAN DEFAULT FALSE,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE lessons (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  course_id   UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  title       TEXT NOT NULL,
  video_url   TEXT,
  sort_order  INT DEFAULT 0,
  duration_s  INT,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE enrollments (
  user_id     UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  course_id   UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
  progress    JSONB DEFAULT '{}',
  enrolled_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (user_id, course_id)
);

-- ============================================================
-- TRIGGERS: auto-update counts
-- ============================================================
CREATE OR REPLACE FUNCTION update_profile_counts()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_TABLE_NAME = 'follows' THEN
    IF TG_OP = 'INSERT' THEN
      UPDATE profiles SET follower_count = follower_count + 1 WHERE id = NEW.following_id;
      UPDATE profiles SET following_count = following_count + 1 WHERE id = NEW.follower_id;
    ELSIF TG_OP = 'DELETE' THEN
      UPDATE profiles SET follower_count = GREATEST(follower_count - 1, 0) WHERE id = OLD.following_id;
      UPDATE profiles SET following_count = GREATEST(following_count - 1, 0) WHERE id = OLD.follower_id;
    END IF;
  ELSIF TG_TABLE_NAME = 'posts' THEN
    IF TG_OP = 'INSERT' THEN
      UPDATE profiles SET post_count = post_count + 1 WHERE id = NEW.creator_id;
    ELSIF TG_OP = 'DELETE' THEN
      UPDATE profiles SET post_count = GREATEST(post_count - 1, 0) WHERE id = OLD.creator_id;
    END IF;
  ELSIF TG_TABLE_NAME = 'likes' THEN
    IF TG_OP = 'INSERT' THEN
      UPDATE posts SET like_count = like_count + 1 WHERE id = NEW.post_id;
    ELSIF TG_OP = 'DELETE' THEN
      UPDATE posts SET like_count = GREATEST(like_count - 1, 0) WHERE id = OLD.post_id;
    END IF;
  ELSIF TG_TABLE_NAME = 'comments' THEN
    IF TG_OP = 'INSERT' THEN
      UPDATE posts SET comment_count = comment_count + 1 WHERE id = NEW.post_id;
    ELSIF TG_OP = 'DELETE' THEN
      UPDATE posts SET comment_count = GREATEST(comment_count - 1, 0) WHERE id = OLD.post_id;
    END IF;
  END IF;
  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_follows_count
  AFTER INSERT OR DELETE ON follows
  FOR EACH ROW EXECUTE FUNCTION update_profile_counts();

CREATE TRIGGER trg_posts_count
  AFTER INSERT OR DELETE ON posts
  FOR EACH ROW EXECUTE FUNCTION update_profile_counts();

CREATE TRIGGER trg_likes_count
  AFTER INSERT OR DELETE ON likes
  FOR EACH ROW EXECUTE FUNCTION update_profile_counts();

CREATE TRIGGER trg_comments_count
  AFTER INSERT OR DELETE ON comments
  FOR EACH ROW EXECUTE FUNCTION update_profile_counts();

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO profiles (id, username, display_name)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'username', 'user_' || LEFT(NEW.id::TEXT, 8)),
    COALESCE(NEW.raw_user_meta_data->>'display_name', NEW.email)
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- ============================================================
-- ROW LEVEL SECURITY
-- ============================================================
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE post_media ENABLE ROW LEVEL SECURITY;
ALTER TABLE follows ENABLE ROW LEVEL SECURITY;
ALTER TABLE likes ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Profiles: public read, own write
CREATE POLICY profiles_select ON profiles FOR SELECT USING (true);
CREATE POLICY profiles_update ON profiles FOR UPDATE USING (auth.uid() = id);

-- Posts: public read (non-adult), own write
CREATE POLICY posts_select ON posts FOR SELECT
  USING (is_adult = FALSE OR creator_id = auth.uid());
CREATE POLICY posts_insert ON posts FOR INSERT
  WITH CHECK (creator_id = auth.uid());
CREATE POLICY posts_update ON posts FOR UPDATE
  USING (creator_id = auth.uid());
CREATE POLICY posts_delete ON posts FOR DELETE
  USING (creator_id = auth.uid());

-- Post media: follow post access
CREATE POLICY post_media_select ON post_media FOR SELECT USING (true);
CREATE POLICY post_media_insert ON post_media FOR INSERT
  WITH CHECK (
    EXISTS (SELECT 1 FROM posts WHERE id = post_id AND creator_id = auth.uid())
  );

-- Follows
CREATE POLICY follows_select ON follows FOR SELECT USING (true);
CREATE POLICY follows_insert ON follows FOR INSERT
  WITH CHECK (follower_id = auth.uid());
CREATE POLICY follows_delete ON follows FOR DELETE
  USING (follower_id = auth.uid());

-- Likes
CREATE POLICY likes_select ON likes FOR SELECT USING (true);
CREATE POLICY likes_insert ON likes FOR INSERT
  WITH CHECK (user_id = auth.uid());
CREATE POLICY likes_delete ON likes FOR DELETE
  USING (user_id = auth.uid());

-- Comments
CREATE POLICY comments_select ON comments FOR SELECT USING (true);
CREATE POLICY comments_insert ON comments FOR INSERT
  WITH CHECK (user_id = auth.uid());
CREATE POLICY comments_delete ON comments FOR DELETE
  USING (user_id = auth.uid());

-- Messages: participants only
CREATE POLICY messages_select ON messages FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM conversation_participants
      WHERE conversation_id = messages.conversation_id AND user_id = auth.uid()
    )
  );
CREATE POLICY messages_insert ON messages FOR INSERT
  WITH CHECK (
    sender_id = auth.uid() AND
    EXISTS (
      SELECT 1 FROM conversation_participants
      WHERE conversation_id = messages.conversation_id AND user_id = auth.uid()
    )
  );

-- Notifications: own only
CREATE POLICY notifications_select ON notifications FOR SELECT
  USING (user_id = auth.uid());
CREATE POLICY notifications_update ON notifications FOR UPDATE
  USING (user_id = auth.uid());

-- ============================================================
-- REALTIME (enable for messages)
-- ============================================================
ALTER PUBLICATION supabase_realtime ADD TABLE messages;

-- ============================================================
-- STORAGE BUCKETS (run in Supabase Dashboard or via API)
-- ============================================================
-- INSERT INTO storage.buckets (id, name, public) VALUES ('avatars', 'avatars', true);
-- INSERT INTO storage.buckets (id, name, public) VALUES ('posts', 'posts', true);
-- INSERT INTO storage.buckets (id, name, public) VALUES ('adult', 'adult', false);
