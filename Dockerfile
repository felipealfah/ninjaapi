# Use an official Python runtime as a parent image
FROM python:3.10.12-slim

# Set the working directory in the container
WORKDIR /ninja

# Install necessary system utilities, libraries, and dependencies for Selenium
RUN apt-get update && apt-get install -y \
    cron \
    tzdata \
    wget \
    gnupg \
    software-properties-common \
    unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add Google Chrome repository and install it
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Download and install ChromeDriver
RUN wget https://chromedriver.storage.googleapis.com/100.0.4896.60/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/bin/chromedriver && \
    rm chromedriver_linux64.zip

# Set the timezone to America/Sao_Paulo
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy cron job definition into the container
COPY cron-jobs /etc/cron.d/cron-jobs

# Copy Python scripts and ETL directory into the container
COPY diario.py semanal.py quinzenal.py app.py ./
COPY etl ./etl

# Copy the api_ninjapresell directory into the container
COPY api_ninjapresell ./api_ninjapresell

# Copy the .env file into the container
COPY .env .env

# Copy the start script
COPY start.sh ./
RUN chmod +x start.sh

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Expose the port on which the FastAPI app will run
EXPOSE 8000

# Add cron jobs
RUN chmod 0644 /etc/cron.d/cron-jobs
RUN crontab /etc/cron.d/cron-jobs

# Command to run both cron and FastAPI
CMD ["./start.sh"]
