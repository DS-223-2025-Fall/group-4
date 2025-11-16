-- ====================================================
-- DROP TABLES IF THEY EXIST
-- ====================================================

DROP TABLE IF EXISTS api_logs;
DROP TABLE IF EXISTS prediction_logs;
DROP TABLE IF EXISTS fact_content_features;
DROP TABLE IF EXISTS fact_influencer_performance;
DROP TABLE IF EXISTS audience_demographics;
DROP TABLE IF EXISTS engagement;
DROP TABLE IF EXISTS content;
DROP TABLE IF EXISTS influencers;

-- ====================================================
-- CREATE TABLES
-- ====================================================

-- =======================
-- CORE TABLES
-- =======================
CREATE TABLE influencers (
    influencer_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    username VARCHAR(255),
    platform VARCHAR(50),
    follower_count INT,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE content (
    content_id SERIAL PRIMARY KEY,
    influencer_id INT REFERENCES influencers(influencer_id) ON DELETE CASCADE,
    content_type VARCHAR(50),
    topic VARCHAR(100),
    post_date DATE,
    caption TEXT,
    url TEXT
);

CREATE TABLE engagement (
    engagement_id SERIAL PRIMARY KEY,
    content_id INT REFERENCES content(content_id) ON DELETE CASCADE,
    likes INT,
    comments INT,
    shares INT,
    views INT,
    engagement_rate FLOAT
);

CREATE TABLE audience_demographics (
    audience_id SERIAL PRIMARY KEY,
    influencer_id INT REFERENCES influencers(influencer_id) ON DELETE CASCADE,
    age_group VARCHAR(50),
    gender VARCHAR(20),
    country VARCHAR(100),
    percentage FLOAT
);

-- =======================
-- DATA SCIENCE / FEATURE TABLES
-- =======================
CREATE TABLE fact_influencer_performance (
    id SERIAL PRIMARY KEY,
    influencer_id INT REFERENCES influencers(influencer_id) ON DELETE CASCADE,
    avg_engagement_rate FLOAT,
    avg_likes FLOAT,
    avg_comments FLOAT,
    avg_shares FLOAT,
    avg_views FLOAT,
    follower_count INT,
    category VARCHAR(100),
    audience_top_country VARCHAR(100)
);

CREATE TABLE fact_content_features (
    id SERIAL PRIMARY KEY,
    content_id INT REFERENCES content(content_id) ON DELETE CASCADE,
    influencer_id INT REFERENCES influencers(influencer_id) ON DELETE CASCADE,
    tag_count INT,
    caption_length INT,
    content_type VARCHAR(50),
    engagement_rate FLOAT
);

-- =======================
-- LOGGING TABLES
-- =======================
CREATE TABLE prediction_logs (
    log_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    influencer_id INT REFERENCES influencers(influencer_id),
    content_id INT REFERENCES content(content_id),
    predicted_engagement FLOAT,
    model_version VARCHAR(50)
);

CREATE TABLE api_logs (
    log_id SERIAL PRIMARY KEY,
    "user" VARCHAR(255),
    endpoint VARCHAR(255),
    status VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

