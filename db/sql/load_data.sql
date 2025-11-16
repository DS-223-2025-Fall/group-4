COPY influencers(influencer_id, name, username, platform, follower_count, category, created_at)
FROM '${CSV_FOLDER}/influencers.csv' DELIMITER ',' CSV HEADER;

COPY content(content_id, influencer_id, content_type, topic, post_date, caption, url)
FROM '${CSV_FOLDER}/content.csv' DELIMITER ',' CSV HEADER;

COPY engagement(engagement_id, content_id, likes, comments, shares, views, engagement_rate)
FROM '${CSV_FOLDER}/engagement.csv' DELIMITER ',' CSV HEADER;

COPY audience_demographics(audience_id, influencer_id, age_group, gender, country, percentage)
FROM '${CSV_FOLDER}/audience_demographics.csv' DELIMITER ',' CSV HEADER;

