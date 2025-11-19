# ---- Base Image ----
FROM python:3.12-slim-bullseye

# Avoid interactive prompts and fix flaky apt mirrors
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies with retry logic
RUN apt-get clean && rm -rf /var/lib/apt/lists/* && \
    echo 'Acquire::Retries "5";' > /etc/apt/apt.conf.d/80-retries && \
    echo 'Acquire::http::No-Cache "true";' > /etc/apt/apt.conf.d/no-cache && \
    echo 'Acquire::http::Pipeline-Depth "0";' > /etc/apt/apt.conf.d/pipeline && \
    apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libfreetype6-dev \
        libpng-dev \
        libjpeg-dev \
        libblas-dev \
        liblapack-dev \
        gfortran \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ---- App Setup ----
WORKDIR /etl

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade -r requirements.txt &&\
    pip freeze > requirements.txt
# Copy application files
COPY . .

# Expose port for FastAPI/ETL API
EXPOSE 3000

# ---- Default Command ----
CMD ["python", "etl.py"]