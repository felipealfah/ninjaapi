# Use an official Python runtime as a parent image
FROM python:3.10.12

# Set the working directory in the container
WORKDIR /ninja

# Copy the current directory contents into the container at /ninja
COPY . /ninja

# Create a directory for logs
RUN mkdir __logger

# Install necessary utilities
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    xvfb

# Configuration of environment variables
ENV DISPLAY=:99

# Upgrade pip and install required Python packages
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port 80 to the host machine
EXPOSE 80

# Define environment variable to specify the port Flask should listen on
ENV FLASK_RUN_PORT 80

# Default command to start the application
CMD ["python", "./app.py"]
