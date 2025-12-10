# Streamlit Application Documentation

The Predictfluence frontend is built with Streamlit, providing an interactive web interface for managing influencer marketing campaigns.

## Access

- **URL**: http://localhost:8501
- **Port**: 8501 (configurable in `docker-compose.yml`)

## Features

### 1. Login Page
- Email/password authentication
- Demo mode for quick preview
- User profile creation

### 2. Dashboard
**Purpose**: High-level overview of marketing operations

**Features:**
- **KPIs**:
  - Total Campaigns count
  - Total Influencers count
  - Average Engagement Rate
  - Average Cost per Influencer
- **Charts**:
  - Engagement trends over time (30 days)
  - Top performing campaigns (bar chart)

**Data Sources:**
- `GET /campaigns`
- `GET /influencers/count`
- `GET /analytics/performance`
- `GET /analytics/engagement?range=30d`
- `GET /analytics/top-campaigns?limit=5`

### 3. Influencers Page
**Purpose**: Browse and discover influencers

**Features:**
- **Filters**:
  - Platform (Instagram, TikTok, YouTube, All)
  - Category dropdown
  - Follower range slider
  - Search by name/username
- **View Modes**:
  - Table view: Sortable data table
  - Card view: Visual influencer cards
- **Influencer Details**:
  - Profile information (Name, Handle, Platform, Followers, Category)
  - Performance metrics (Avg Engagement Rate, Avg Likes, Avg Views)

**Data Sources:**
- `GET /influencers` (with filters, page_size=200 to show all influencers)
- `GET /influencers/{id}?include=performance`

### 4. Campaigns Page
**Purpose**: Manage marketing campaigns

**Features:**
- Create new campaigns with brand, objective, dates, budget, and status
- Campaign selection dropdown
- Campaign summary:
  - Budget, status
  - Influencer count
  - Average engagement rate
  - Average views
- Linked Influencers & Content table:
  - Performance metrics per influencer
  - Role (primary/supporting)
  - Paid status
  - Engagement metrics (likes, comments, views)

**Data Sources:**
- `GET /campaigns`
- `GET /campaigns/{id}/summary`
- `GET /campaigns/{id}/influencer-performance`

### 5. Recommendations Page
**Purpose**: AI-powered influencer recommendations

**Features:**
- **Filters**:
  - Platform selection (Instagram, TikTok, YouTube, Facebook)
  - Audience size band (1k-10k, 10k-100k, 100k-500k, 500k+)
  - Content type (Video, Reel/Shorts, Story, Image/Carousel, Live)
  - Category (Beauty, Fashion, Lifestyle, Tech, Gaming, Travel, Food, Fitness, Finance, Music)
- **Results**:
  - Top 10 recommended influencers
  - Predicted engagement rate
  - Rationale for recommendation
  - View Details button to see full influencer profile
  - Hire button to directly assign influencer to a campaign

**Data Sources:**
- `POST /recommendations`

### 6. Insights Page
**Purpose**: Advanced analytics and data exploration

**Features:**
- **Audience Analytics Tab**:
  - Demographics breakdown
  - Group by: Country, Age Group, Gender
  - Interactive bar charts
- **Creative Performance Tab**:
  - Engagement by content type
  - Engagement by topic
  - Performance comparison charts

**Data Sources:**
- `GET /analytics/audience?group_by={dimension}`
- `GET /analytics/creative`

### 7. Demo Intro Page
**Purpose**: Introduction and overview of the platform

**Features:**
- Hero section with title and tagline
- Problem/Solution/Outcome overview
- Demo checklist showing what will be covered
- Key reassurance about ML-powered recommendations

## Technical Details

### Architecture
- **Framework**: Streamlit
- **Language**: Python 3.12
- **API Client**: Custom `pages/api.py` module
- **Styling**: Custom CSS via `pages/components.py`

### API Integration
All API calls go through the centralized `pages/api.py` module:
- Automatic error handling
- Request/response logging
- Demo mode fallbacks
- Retry logic

### State Management
Uses Streamlit's session state:
- `authenticated`: User login status
- `demo_mode`: Demo mode flag
- `auth_token`: Authentication token
- `page`: Current page navigation

### Error Handling
- Graceful degradation on API errors
- User-friendly error messages
- Fallback to demo data when available
- Defensive checks for API response formats

## Development

### Running Locally
```bash
cd Predictfluence/app
pip install -r requirements.txt
export API_URL=http://localhost:8008
streamlit run app.py
```

### File Structure
```
app/
├── app.py              # Main entry point, navigation
├── pages/
│   ├── api.py          # API client wrapper
│   ├── components.py   # Reusable UI components
│   ├── demo.py         # Demo intro page
│   ├── dashboard.py    # Dashboard page
│   ├── influencers.py  # Influencers page
│   ├── campaigns.py    # Campaigns page
│   ├── recommendations.py  # Recommendations page
│   └── insights.py     # Insights page
└── requirements.txt    # Python dependencies
```

### Adding New Pages
1. Create `pages/new_page.py`
2. Define `render(api_url: str)` function
3. Add to `PAGES` dict in `app.py`
4. Update sidebar navigation

## UI Components

### Reusable Components
- `kpi_card(title, value)`: KPI display card
- `placeholder_section(title)`: Section container
- `inject_styles()`: Global theme styles

### Styling
- Material Design inspired
- Responsive layout
- Custom color scheme (teal/blue gradient)
- Card-based UI elements

## Demo Mode

When demo mode is enabled:
- Skips authentication
- Uses synthetic data
- Shows all features
- Useful for demonstrations and testing

Enable via:
- Login page: "Preview All Pages" button
- Sidebar: "Preview All Pages (Demo)" button

## Production Considerations

### Security
- Implement proper authentication
- Add CSRF protection
- Sanitize user inputs
- Rate limiting

### Performance
- Cache API responses
- Lazy load data
- Pagination for large lists
- Optimize chart rendering

### Monitoring
- Error tracking (Sentry)
- Usage analytics
- Performance monitoring
- User feedback collection

---

For API documentation, see [API Documentation](api.md)
