# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt first (for efficient Docker caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8050

# Start the Dash app using Gunicorn for production
CMD ["gunicorn", "-b", "0.0.0.0:8050", "app:server"]
