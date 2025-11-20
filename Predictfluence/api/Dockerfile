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
    
    # set work directory
    WORKDIR /api
    
    # install dependencies
    COPY requirements.txt .
    RUN pip3 install --upgrade pip
    RUN pip install -r requirements.txt
    
    # copy project
    COPY . .
    
    # Expose the port FastAPI will run on
    EXPOSE 8000
    
    # Command to run the app
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    