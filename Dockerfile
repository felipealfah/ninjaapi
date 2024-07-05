# Use an official Python runtime as a parent image
FROM python:3.10.12-slim

# Set the working directory in the container
WORKDIR /ninja

# Install necessary system utilities and libraries
RUN apt-get update && apt-get install -y \
    cron \
    tzdata \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the timezone to America/Sao_Paulo
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy cron job definition into the container
COPY cron-jobs /etc/cron.d/cron-jobs

# Copy Python scripts and ETL directory into the container
COPY diario.py semanal.py quinzenal.py ./
COPY etl ./etl

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Add cron jobs
RUN chmod 0644 /etc/cron.d/cron-jobs
RUN crontab /etc/cron.d/cron-jobs

# Start cron service
CMD ["cron", "-f"]
