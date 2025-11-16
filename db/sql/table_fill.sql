-- fact_influencer_performance: aggregate engagement per influencer
INSERT INTO fact_influencer_performance (influencer_id, total_posts, avg_likes, avg_comments, avg_shares, avg_engagement_rate)
SELECT
    i.influencer_id,
    COUNT(c.content_id) AS total_posts,
    COALESCE(AVG(e.likes), 0) AS avg_likes,
    COALESCE(AVG(e.comments), 0) AS avg_comments,
    COALESCE(AVG(e.shares), 0) AS avg_shares,
    COALESCE(AVG(e.engagement_rate), 0) AS avg_engagement_rate
FROM influencers i
LEFT JOIN content c ON i.influencer_id = c.influencer_id
LEFT JOIN engagement e ON c.content_id = e.content_id
GROUP BY i.influencer_id;

-- fact_content_features: direct mapping from content + engagement
INSERT INTO fact_content_features (content_id, likes, comments, shares, engagement_rate)
SELECT
    c.content_id,
    COALESCE(e.likes, 0) AS likes,
    COALESCE(e.comments, 0) AS comments,
    COALESCE(e.shares, 0) AS shares,
    COALESCE(e.engagement_rate, 0) AS engagement_rate
FROM content c
LEFT JOIN engagement e ON c.content_id = e.content_id;

