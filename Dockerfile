# ============================================================
# Dockerfile — packages the API into a portable container
# ============================================================
# WHAT THIS DOES:
#   1. Starts from a slim Python base image
#   2. Copies your code and installs dependencies
#   3. Runs the API with Gunicorn (production-grade server)
#
# BUILD:  docker build -t task-api .
# RUN:    docker run -p 5000:5000 task-api
# ============================================================

FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements first (Docker caches this layer if requirements don't change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY app_main.py .

# Expose the port the app runs on
EXPOSE 5000

# Use Gunicorn for production (not Flask's dev server)
# "app_main:create_app()" tells Gunicorn to use your factory function
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app_main:create_app()"]
