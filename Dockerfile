# Use an official Python runtime as a parent image
FROM python:3.10.12

# Set the working directory in the container
WORKDIR /ninja

# Copy the current directory contents into the container at /ninja
COPY . /ninja

# Create a directory for logs, if necessary
RUN mkdir __logger

# Install necessary system utilities and libraries
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    xvfb \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Configuration of environment variables for headless operation
ENV DISPLAY=:99

# Upgrade pip and install required Python packages
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install gunicorn

# Expose port 80 to the host machine for external access
EXPOSE 80

# Define environment variable to specify the port Flask should listen on
ENV FLASK_RUN_PORT 80

# Command to start the application using Gunicorn on port 80
CMD ["gunicorn", "-b", "0.0.0.0:80", "app:app"]
