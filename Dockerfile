# ===============================
# Dockerfile for Fraud Detection API
# ===============================

# Start from an official lightweight Python image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy only requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
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
