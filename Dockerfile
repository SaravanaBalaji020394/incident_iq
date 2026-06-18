# Use an official lightweight Python runtime as a parent image
FROM python:3.11-slim

# Set system environment variables to optimize Python behavior inside Docker
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files to disk
# PYTHONUNBUFFERED: Forces standard output streams to flush instantly to terminal logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies needed for compiling certain python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file first to maximize Docker layer caching
COPY requirements.txt /app/

# Install dependencies directly into the container's system space
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire local project directory contents into the container
COPY . /app/

# Expose port 8000 to allow traffic into the FastAPI gateway application
EXPOSE 8000

# Fire up the Uvicorn web server spinning up our API interface layer
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "0.0.0.0"]