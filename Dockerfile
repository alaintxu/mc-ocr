# Use an official Python runtime as a parent image
FROM python:3.11-bookworm

# Set the working directory in the container to /app
WORKDIR /app

# Install Tesseract
RUN apt-get update \
    && apt-get install -y tesseract-ocr tesseract-ocr-spa pipx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pipx install uv

COPY pyproject.toml .
COPY uv.lock .

RUN uv sync

# Copy only requirements to cache them in docker layer
#COPY requirements.txt ./

# Install project dependencies
#RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . /app

# Make port 80 available to the world outside this container
EXPOSE 80

# Run the application using uvicorn
CMD ["granian", "--interface", "asgi", "main:app"]