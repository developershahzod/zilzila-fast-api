FROM python:3.9-slim

WORKDIR /app

# Install PostgreSQL client for the wait script
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make the wait script executable
RUN chmod +x wait-for-db.sh

# Expose the port the app runs on
EXPOSE 8005

# Command to run the application
CMD ["./wait-for-db.sh", "db", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]
