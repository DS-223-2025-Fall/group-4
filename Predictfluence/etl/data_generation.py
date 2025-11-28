"""
Synthetic CSV Generator for Influencer Marketing Demo Data

This script generates realistic synthetic CSV files for testing and development
of an influencer marketing analytics project. The generated CSVs include:

1. influencers.csv: Profiles of social media influencers with follower counts,
   categories, and platform information.
2. content.csv: Posts created by influencers including type, topic, captions, and URLs.
3. engagement.csv: Engagement metrics for each content item such as likes, comments,
   shares, views, and computed engagement rate.
4. audience_demographics.csv: Audience breakdown by age group, gender, country, and percentage.
5. brands.csv: Brand profiles with industry, country, and creation date.
6. campaigns.csv: Marketing campaigns by brands, with objectives, budgets, dates, and status.
7. users.csv: Demo users for API or admin testing, including emails, hashed passwords, roles, and company.

Key Features:
- Generates synthetic data using Faker and NumPy for realistic distributions.
- Engagement metrics are calculated based on influencer follower count.
- CSV output folder is automatically created relative to the script location.
- Configurable parameters for number of influencers, posts, brands, and campaigns.
- Fully self-contained for local development and testing without external data dependencies.

Usage:
Simply run the script to populate the CSV_FOLDER (default: "data") with all CSV files:
    cd etl
    python Database/data_generation.py

Dependencies:
- pandas
- faker
- numpy
- python-dotenv
"""

import pandas as pd
from faker import Faker
import random
import os
import numpy as np
import dotenv
from datetime import timedelta

dotenv.load_dotenv()
fake = Faker()

# ----------------------------
# PARAMETERS
# ----------------------------
NUM_INFLUENCERS = 30
MIN_POSTS = 2
MAX_POSTS = 30
NUM_BRANDS = 5
MIN_CAMPAIGNS = 1
MAX_CAMPAIGNS = 3
MAX_LINKS_PER_CAMPAIGN = 8

PLATFORMS = ["Instagram", "TikTok", "YouTube"]
CATEGORIES = ["Beauty", "Fitness", "Tech", "Food", "Travel", "Gaming"]
CONTENT_TYPES = ["Image", "Video", "Reel", "Story"]
TOPICS = ["Fitness", "Beauty", "Tech", "Food", "Travel", "Gaming"]
AGE_GROUPS = ["13-17", "18-24", "25-34", "35-44", "45-54", "55+"]
GENDERS = ["Male", "Female", "Other"]
COUNTRIES = ["USA", "UK", "Canada", "Germany", "France", "India", "Brazil"]
CAMPAIGN_STATUS = ["planned", "active", "completed"]

# ----------------------------
# OUTPUT FOLDER
# ----------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
output_folder = os.path.join(script_dir, os.getenv("CSV_FOLDER", "data"))
os.makedirs(output_folder, exist_ok=True)

# ----------------------------
# 1. influencers
# ----------------------------
influencers = []
for i in range(1, NUM_INFLUENCERS + 1):
    follower_count = int(np.random.lognormal(mean=8, sigma=1))
    influencers.append({
        "influencer_id": i,
        "name": fake.name(),
        "username": fake.user_name(),
        "platform": random.choice(PLATFORMS),
        "follower_count": follower_count,
        "category": random.choice(CATEGORIES),
        "created_at": fake.date_this_decade()
    })
df_influencers = pd.DataFrame(influencers)
df_influencers.to_csv(os.path.join(output_folder, "influencers.csv"), index=False)

# ----------------------------
# 2. content
# ----------------------------
contents = []
content_id_counter = 1
for influencer in influencers:
    num_posts = random.randint(MIN_POSTS, MAX_POSTS)
    for _ in range(num_posts):
        contents.append({
            "content_id": content_id_counter,
            "influencer_id": influencer["influencer_id"],
            "content_type": random.choices(CONTENT_TYPES, weights=[0.4, 0.3, 0.2, 0.1])[0],
            "topic": random.choice(TOPICS),
            "post_date": fake.date_this_year(),
            "caption": fake.sentence(nb_words=random.randint(5, 20)),
            "url": fake.url()
        })
        content_id_counter += 1
df_content = pd.DataFrame(contents)
df_content.to_csv(os.path.join(output_folder, "content.csv"), index=False)

# ----------------------------
# 3. engagement
# ----------------------------
engagements = []
for content in contents:
    influencer = next(i for i in influencers if i["influencer_id"] == content["influencer_id"])
    followers = influencer["follower_count"]

    likes = max(0, int(random.gauss(followers * 0.03, 50)))
    comments = max(0, int(likes * random.uniform(0.05, 0.2)))
    shares = max(0, int(likes * random.uniform(0.01, 0.05)))
    views = max(likes + comments, int(random.gauss(followers * random.uniform(0.1, 0.5), 100)))
    engagement_rate = round((likes + comments + shares) / max(1, views), 4)

    engagements.append({
        "engagement_id": content["content_id"],
        "content_id": content["content_id"],
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "views": views,
        "engagement_rate": engagement_rate
    })
df_engagement = pd.DataFrame(engagements)
df_engagement.to_csv(os.path.join(output_folder, "engagement.csv"), index=False)

# ----------------------------
# 4. audience_demographics
# ----------------------------
audience_list = []
audience_id_counter = 1
for influencer in influencers:
    num_segments = random.randint(2, 5)
    selected_countries = random.sample(COUNTRIES, k=num_segments)
    for country in selected_countries:
        audience_list.append({
            "audience_id": audience_id_counter,
            "influencer_id": influencer["influencer_id"],
            "age_group": random.choice(AGE_GROUPS),
            "gender": random.choice(GENDERS),
            "country": country,
            "percentage": round(random.uniform(5, 50), 2)
        })
        audience_id_counter += 1
df_audience = pd.DataFrame(audience_list)
df_audience.to_csv(os.path.join(output_folder, "audience_demographics.csv"), index=False)

# ----------------------------
# 5. brands
# ----------------------------
brands = []
for i in range(1, NUM_BRANDS + 1):
    brands.append({
        "brand_id": i,
        "name": fake.company(),
        "industry": random.choice(CATEGORIES),
        "country": random.choice(COUNTRIES),
        "created_at": fake.date_this_decade()
    })
df_brands = pd.DataFrame(brands)
df_brands.to_csv(os.path.join(output_folder, "brands.csv"), index=False)

# ----------------------------
# 6. campaigns
# ----------------------------
campaigns = []
campaign_id_counter = 1
for brand in brands:
    num_campaigns = random.randint(MIN_CAMPAIGNS, MAX_CAMPAIGNS)
    for _ in range(num_campaigns):
        start_date = fake.date_this_year()
        end_date = start_date + timedelta(days=random.randint(7, 60))
        campaigns.append({
            "campaign_id": campaign_id_counter,
            "brand_id": brand["brand_id"],
            "name": f"{brand['name']} Campaign {campaign_id_counter}",
            "objective": random.choice(["Brand Awareness", "Engagement", "Sales"]),
            "start_date": start_date,
            "end_date": end_date,
            "budget": round(random.uniform(1000, 50000), 2),
            "status": random.choice(CAMPAIGN_STATUS),
            "created_at": fake.date_this_decade()
        })
        campaign_id_counter += 1
df_campaigns = pd.DataFrame(campaigns)
df_campaigns.to_csv(os.path.join(output_folder, "campaigns.csv"), index=False)

# ----------------------------
# 7. campaign_content
# ----------------------------
campaign_links = []
link_id = 1
for campaign in campaigns:
    # randomly attach some content rows to each campaign
    eligible = random.sample(contents, k=min(len(contents), MAX_LINKS_PER_CAMPAIGN))
    for content in eligible:
        campaign_links.append({
            "id": link_id,
            "campaign_id": campaign["campaign_id"],
            "content_id": content["content_id"],
            "role": random.choice(["primary", "supporting"]),
            "is_paid": random.choice([True, False]),
            "cost": round(random.uniform(50, 800), 2)
        })
        link_id += 1
df_campaign_content = pd.DataFrame(campaign_links)
df_campaign_content.to_csv(os.path.join(output_folder, "campaign_content.csv"), index=False)

# ----------------------------
# 8. users
# ----------------------------
users = []
NUM_USERS = 10
for i in range(1, NUM_USERS + 1):
    users.append({
        "user_id": i,
        "email": fake.unique.email(),
        "hashed_password": fake.password(length=12),
        "role": random.choice(["admin", "analyst", "viewer"]),
        "company": fake.company(),
        "full_name": fake.name(),
        "created_at": fake.date_this_decade()
    })
df_users = pd.DataFrame(users)
df_users.to_csv(os.path.join(output_folder, "users.csv"), index=False)

print(f"CSV files generated in {output_folder}/")
