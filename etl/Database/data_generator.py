from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

def generate_influencer(i):
    platforms = ["Instagram", "TikTok", "YouTube"]
    categories = ["Beauty", "Fitness", "Tech", "Lifestyle", "Travel"]

    return {
        "influencer_id": i,
        "name": fake.name(),
        "username": fake.user_name(),
        "platform": random.choice(platforms),
        "follower_count": random.randint(1000, 500000),
        "category": random.choice(categories),
        "created_at": datetime.now() - timedelta(days=random.randint(1, 1000))
    }


def generate_content(content_id, influencer_id):
    content_types = ["Reel", "Post", "Story", "Video"]
    topics = ["Skincare", "Tech review", "Outfit", "Workout", "Travel tips"]

    return {
        "content_id": content_id,
        "influencer_id": influencer_id,
        "content_type": random.choice(content_types),
        "caption": fake.sentence(),
        "post_date": fake.date_between(start_date="-1y", end_date="today"),
        "url": fake.url()
    }


def generate_engagement(engagement_id, content_id):
    likes = random.randint(10, 20000)
    comments = random.randint(0, 1500)
    shares = random.randint(0, 500)
    views = random.randint(likes, likes * 20)

    # simple formula for dummy engagement rate:
    engagement_rate = (likes + comments + shares) / max(views, 1)

    return {
        "engagement_id": engagement_id,
        "content_id": content_id,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "views": views,
        "engagement_rate": engagement_rate
    }