# Set base Python version for the Docker image
ARG PYTHON_VERSION=3.12

# Use an official lightweight Python runtime as a base image
FROM python:${PYTHON_VERSION}-slim AS base
# Update package lists and install Git
RUN apt-get update && apt-get install -y git

# Create a dedicated volume in the container to persist data
VOLUME /app/data

# Set the default working directory for any RUN, CMD, ENTRYPOINT, COPY, and ADD commands
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install system dependencies required for the project
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    linux-headers-generic \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Download and install Google Chrome for testing purposes
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# Create and activate a Python virtual environment
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Upgrade pip and install Python dependencies from requirements file
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

# Set environment variables for the application
ENV GH_TOKEN ${GH_TOKEN}
ENV ENV "TEST"

# Run an initial Python script to setup or migrate data
RUN python get_started.py

# Define the tests stage with specific environment setup for running tests
FROM base as tests
ENV CHROME_BIN=/usr/bin/google-chrome
ENV PATH="/usr/lib/chromium/:$PATH"
ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV ENV_ROOT_DIRECTORY "/app"
WORKDIR /app
CMD ["pytest"]

# Define the behave stage with environment setup for running behavior-driven tests
FROM base as behave
ENV PYTHONPATH "${PYTHONPATH}:/app:/app/demo"
ENV ENV_ROOT_DIRECTORY "/app"
ENV DISPLAY=:99
WORKDIR /app/demo/testing/example_features_webdriver
CMD ["behave"]
