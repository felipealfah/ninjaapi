# Use an official Python runtime as a parent image
FROM python:3.10.12-slim

# Set the working directory in the container
WORKDIR /ninja

# Copy only the necessary dependency specifications
COPY requirements.txt /ninja/

# Install any needed packages specified in requirements.txt
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    xvfb \
    && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb || apt-get install -f -y \
    && wget https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip -d /usr/local/bin/ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Upgrade pip and install required Python packages
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Expose port 80 to the host machine for external access
EXPOSE 80

# Define environment variable to specify the port FastAPI should listen on
ENV PORT 80

# Copy the rest of your application's code
COPY . /ninja

# Command to start the application using Gunicorn on port 80 with Uvicorn workers
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", ":80", "app:app"]
