FROM python:3.11-slim

# Prevents Python from writing .pyc files and forces immediate log flushing
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies 
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project code into the container
COPY . .

# Command to start the application
CMD ["uvicorn", "main:app", "--app-dir", "Backend", "--host", "0.0.0.0", "--port", "8000", "--reload"]