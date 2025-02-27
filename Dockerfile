FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create config directory from sample if it doesn't exist
RUN if [ ! -d "config" ]; then cp -r config_sample config; fi

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHON_ENV=production
ENV PORT=8000

# Expose the port your application runs on
EXPOSE ${PORT}

# Initialize and run the application
CMD ["sh", "-c", "python -m framework.main"] 