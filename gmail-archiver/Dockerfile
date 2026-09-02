# Use a lightweight, official Python image
FROM python:3.11-slim

# Set system-level security and performance optimizations
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (sqlite3 comes pre-installed in Python images, 
# but this ensures system utilities are up-to-date)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements first to leverage Docker's caching layer
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
#COPY . .
COPY src/ ./

# Run your script when the container starts
CMD ["python", "save_email_to_db.py"]
