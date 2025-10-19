# ===============================
# Dockerfile for Fraud Detection API
# ===============================

# Start from an official lightweight Python image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy only requirements first (for better caching)
COPY requirements.txt .

# Install system build dependencies required by some Python packages
# (these are intentionally minimal; add more libs if a package needs them)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Ensure pip, setuptools and wheel are up-to-date so PEP 517 backends work
RUN python -m pip install --upgrade pip setuptools wheel

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Environment variables for model and scaler paths
ENV MODEL_PATH=models/run_local/model.joblib
ENV SCALER_PATH=data/features/scaler.joblib

# Default command to start the FastAPI app
CMD ["uvicorn", "src.serve:app", "--host", "0.0.0.0", "--port", "8000"]
