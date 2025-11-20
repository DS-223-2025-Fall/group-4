# ---- Base Image (Stable for Streamlit) ----
FROM python:3.12-slim-bullseye

# Avoid interactive prompts + Python optimizations
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies required by numpy, pandas, streamlit, charts
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

# Set working directory
WORKDIR /app

# Copy Python dependency file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into container
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.headless=true", "--server.runOnSave=true"]
