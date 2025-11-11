# Use an official Python runtime as a parent image
FROM python:3.13-slim-bookworm

# Set the working directory in the container to /app
WORKDIR /app

# Install Tesseract
RUN apt-get update \
    && apt-get install -y tesseract-ocr tesseract-ocr-spa \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv using the official installer
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml .

# Sync dependencies (uv will resolve and install)
RUN uv sync

# Copy only requirements to cache them in docker layer
#COPY requirements.txt ./

# Install project dependencies
#RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . /app

# Make port 80 available to the world outside this container
EXPOSE 80

# Run the application using granian
CMD ["uv", "run", "granian", "--interface", "asgi", "--host", "0.0.0.0", "--port", "80", "main:app"]