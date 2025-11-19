# ----------------------------
# CORE TABLES
# ----------------------------
class Influencer:
    table_name = "influencers"
    columns = [
        "influencer_id",
        "name",
        "username",
        "platform",
        "follower_count",
        "category",
        "created_at"
    ]

class Content:
    table_name = "content"
    columns = [
        "content_id",
        "influencer_id",
        "content_type",
        "topic",
        "post_date",
        "caption",
        "url"
    ]
    foreign_keys = {
        "influencer_id": "influencers.influencer_id"
    }

class Engagement:
    table_name = "engagement"
    columns = [
        "engagement_id",
        "content_id",
        "likes",
        "comments",
        "shares",
        "views",
        "engagement_rate"
    ]
    foreign_keys = {
        "content_id": "content.content_id"
    }

class AudienceDemographics:
    table_name = "audience_demographics"
    columns = [
        "audience_id",
        "influencer_id",
        "age_group",
        "gender",
        "country",
        "percentage"
    ]
    foreign_keys = {
        "influencer_id": "influencers.influencer_id"
    }

class Brand:
    table_name = "brands"
    columns = [
        "brand_id",
        "name",
        "industry",
        "country",
        "created_at"
    ]

class Campaign:
    table_name = "campaigns"
    columns = [
        "campaign_id",
        "brand_id",
        "name",
        "objective",
        "start_date",
        "end_date",
        "budget",
        "status",
        "created_at"
    ]
    foreign_keys = {
        "brand_id": "brands.brand_id"
    }

class CampaignContent:
    table_name = "campaign_content"
    columns = [
        "id",
        "campaign_id",
        "content_id",
        "role",
        "is_paid"
    ]
    foreign_keys = {
        "campaign_id": "campaigns.campaign_id",
        "content_id": "content.content_id"
    }

# ----------------------------
# FACT TABLES
# ----------------------------
class FactInfluencerPerformance:
    table_name = "fact_influencer_performance"
    columns = [
        "id",
        "influencer_id",
        "avg_engagement_rate",
        "avg_likes",
        "avg_comments",
        "avg_shares",
        "avg_views",
        "follower_count",
        "category",
        "audience_top_country"
    ]
    foreign_keys = {
        "influencer_id": "influencers.influencer_id"
    }

class FactContentFeatures:
    table_name = "fact_content_features"
    columns = [
        "id",
        "content_id",
        "influencer_id",
        "tag_count",
        "caption_length",
        "content_type",
        "engagement_rate"
    ]
    foreign_keys = {
        "content_id": "content.content_id",
        "influencer_id": "influencers.influencer_id"
    }

# ----------------------------
# LOGGING TABLES
# ----------------------------
class PredictionLogs:
    table_name = "prediction_logs"
    columns = [
        "log_id",
        "timestamp",
        "influencer_id",
        "content_id",
        "predicted_engagement",
        "model_version"
    ]
    foreign_keys = {
        "influencer_id": "influencers.influencer_id",
        "content_id": "content.content_id"
    }

class APILogs:
    table_name = "api_logs"
    columns = [
        "log_id",
        "user",
        "endpoint",
        "status",
        "timestamp"
    ]

# ----------------------------
# OPTIONAL: helper for all tables
# ----------------------------
ALL_TABLES = [
    Influencer,
    Content,
    Engagement,
    AudienceDemographics,
    FactInfluencerPerformance,
    FactContentFeatures,
    PredictionLogs,
    APILogs,
    Brand,
    Campaign,
    CampaignContent
]
