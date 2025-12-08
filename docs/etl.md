# ETL Service Documentation

The ETL (Extract, Transform, Load) service is responsible for populating the database with data from CSV files and generating synthetic data when needed.

## Access

- **Service**: Runs as a Docker container (`etl_service`)
- **Execution**: Runs automatically on startup via `docker compose up`
- **Data Location**: `Predictfluence/etl/data/`

## Overview

The ETL service performs the following operations:

1. **Data Generation**: Creates comprehensive synthetic data if CSV files don't exist
2. **Schema Management**: Drops and recreates database tables to ensure schema consistency
3. **Data Loading**: Loads data from CSV files into PostgreSQL database
4. **Fact Table Population**: Calculates and populates aggregated fact tables
5. **Data Validation**: Performs quality checks on loaded data

## Process Flow

### 1. Startup Sequence

When the ETL service starts:

1. **Check for CSV Files**: Looks for CSV files in `data/` folder
2. **Generate if Missing**: If CSVs don't exist, generates comprehensive synthetic data
3. **Schema Reset**: Drops all existing tables and recreates them
4. **Load Dimension Tables**: Loads base tables (influencers, content, brands, campaigns, etc.)
5. **Calculate Fact Tables**: Populates aggregated fact tables
6. **Validation**: Performs data quality checks

### 2. Data Generation

If CSV files don't exist, the ETL generates:

- **150 Influencers**: Across Instagram, TikTok, YouTube platforms
- **5,000-7,500 Content Posts**: With captions, URLs, dates
- **Engagement Metrics**: Likes, comments, shares, views, engagement rates
- **20 Brands**: Various industries and countries
- **40-100 Campaigns**: With budgets, objectives, statuses
- **Audience Demographics**: Age groups, genders, countries per influencer
- **Campaign-Content Links**: Associations between campaigns and content

### 3. Dimension Tables Loaded

The ETL loads the following dimension tables:

- `influencers`: Core influencer information
- `content`: Content posts with captions and metadata
- `engagement`: Engagement metrics for each content piece
- `audience_demographics`: Demographic breakdowns per influencer
- `brands`: Brand information
- `campaigns`: Marketing campaign details
- `campaign_content`: Links between campaigns and content
- `users`: User accounts

### 4. Fact Tables Calculated

The ETL calculates and populates:

#### `fact_influencer_performance`
Aggregated performance metrics per influencer:
- Average engagement rate
- Average likes, comments, shares, views
- Current follower count
- Category
- Top audience country

#### `fact_content_features`
Content features for ML models:
- Tag count (calculated from captions: `#` and `@` symbols)
- Caption length (character count)
- Content type
- Engagement rate

### 5. Data Transformations

The ETL performs several transformations:

- **Tag Count Calculation**: Extracts and counts hashtags and mentions from captions
- **Caption Length**: Calculates character count of captions
- **Post Datetime**: Converts post dates to datetime (defaults to 12:00 PM if time missing)
- **Engagement Rate**: Calculated as `(likes + comments + shares) / views`
- **Missing Value Handling**: Defaults missing values (e.g., follower_count → 1000, category → "Unknown")

## Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `CSV_FOLDER`: Path to CSV data folder (default: `data`)

### CSV File Structure

CSV files should be placed in `Predictfluence/etl/data/`:

- `influencers.csv`
- `content.csv`
- `engagement.csv`
- `audience_demographics.csv`
- `brands.csv`
- `campaigns.csv`
- `campaign_content.csv`
- `users.csv`

## Data Quality

### Validation Checks

The ETL performs the following validations:

- **Record Counts**: Verifies expected number of records loaded
- **Required Fields**: Ensures critical fields are populated
- **Data Types**: Validates date formats and numeric values
- **Referential Integrity**: Ensures foreign key relationships are valid

### Error Handling

- **Graceful Failures**: Continues processing if individual records fail
- **Logging**: Prints detailed progress and error messages
- **Schema Errors**: Handles table creation conflicts gracefully

## Running the ETL

### Automatic Execution

The ETL runs automatically when you start Docker Compose:

```bash
docker compose up
```

The ETL service:
- Waits for database to be healthy
- Runs once and exits (`restart: "no"`)
- Logs output to console

### Manual Execution

To run ETL manually:

```bash
# Inside the ETL container
docker compose exec etl python etl.py

# Or run directly
cd Predictfluence/etl
python etl.py
```

## Dependencies

The ETL service requires:

- `pandas`: Data manipulation
- `sqlalchemy`: Database ORM
- `faker`: Synthetic data generation
- `numpy`: Numerical operations
- `psycopg2-binary`: PostgreSQL driver

## Output

After successful execution, the ETL:

- Populates all database tables
- Prints summary statistics:
  - Number of records loaded per table
  - Fact table record counts
  - Data quality metrics

## Troubleshooting

### ETL Not Running

- Check database is healthy: `docker compose ps`
- Check ETL logs: `docker compose logs etl`
- Verify `DATABASE_URL` is correct in `.env`

### Data Not Loading

- Check CSV files exist in `data/` folder
- Verify CSV file formats match expected schema
- Check database connection string
- Review ETL logs for specific errors

### Schema Errors

- ETL automatically drops and recreates tables
- If errors persist, manually drop tables in pgAdmin
- Check for foreign key constraint violations

## Integration

The ETL service integrates with:

- **Database Service**: Populates PostgreSQL tables
- **API Service**: Provides data for API endpoints
- **DS Service**: Provides training data for ML models

The ETL must complete before:
- API service can serve data
- DS service can train models

Docker Compose handles this via `depends_on` with health checks.

---

For database schema details, see [Database Documentation](database.md)

