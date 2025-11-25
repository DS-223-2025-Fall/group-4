# ---- Base Image ----
FROM python:3.12-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies with retries
RUN apt-get clean && rm -rf /var/lib/apt/lists/* && \
    echo 'Acquire::Retries "5";' > /etc/apt/apt.conf.d/80-retries && \
    echo 'Acquire::http::No-Cache "true";' > /etc/apt/apt.conf.d/no-cache && \
    echo 'Acquire::http::Pipeline-Depth "0";' > /etc/apt/apt.conf.d/pipeline && \
    apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libblas-dev \
        liblapack-dev \
        gfortran \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ds

COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8010

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010"]

