# Fraud Detection ML API & MLOps Pipeline

## Project Overview

This project aims to build, deploy, and monitor a machine learning solution for fraud detection in financial transactions. It demonstrates a full MLOps workflow, including data engineering, model training, API serving, cloud deployment, and infrastructure-as-code.

### Goals

- Detect fraudulent transactions using machine learning
- Provide a robust, production-ready API for real-time scoring
- Enable automated deployment to Azure ML and Kubernetes
- Ensure reproducibility and maintainability with MLOps best practices

## Architecture

- **Data Pipeline**: Raw transaction data is processed and feature-engineered in `src/features.py` and `src/generate_data.py`.
- **Model Training**: The model is trained using scikit-learn in `src/train.py`, with outputs saved as `model.joblib`.
- **API Service**: The FastAPI app in `src/serve.py` loads the trained model and exposes a `/predict` endpoint for scoring.
- **Deployment**: The solution can be deployed locally (Docker, Uvicorn), to Azure ML managed endpoints (`deployment.yml`), or Kubernetes (`k8s/deployment.yaml`).
- **Infrastructure-as-Code**: Azure resources are provisioned using Bicep (`iac/azure_bicep_example.bicep`).
- **Monitoring**: Drift and model performance monitoring scripts are in `scripts/drift_monitor.py`.

## Developer Guide

### Local Development

1. **Install dependencies**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
2. **Start API locally**:
   ```powershell
   uvicorn src.serve:app --host 127.0.0.1 --port 8080
   ```
3. **Test endpoint**:
   ```powershell
   Invoke-RestMethod -Uri 'http://127.0.0.1:8080/predict' `
     -Method POST `
     -ContentType 'application/json' `
     -Body '{"features": {"amount": 100, "hour_of_day": 14, "avg_monthly_spend": 500, "customer_tenure_days": 365, "num_prev_tx_24h": 5}}'
   ```

### Azure ML Deployment

- Update `environment.yml` and `deployment.yml` as needed.
- Deploy with:
  ```powershell
  az ml online-deployment create `
    --file deployment.yml `
    --resource-group <resource-group> `
    --workspace-name <workspace-name>
  ```

### Docker & Kubernetes

- Build Docker image:
  ```powershell
  docker build -t fraud-api:latest .
  ```
- Run container:
  ```powershell
  docker run -p 8080:8080 fraud-api:latest
  ```
- Deploy to Kubernetes using `k8s/deployment.yaml`.

## File Structure

- `src/` - Source code (features, training, serving)
- `data/` - Raw and processed data
- `models/` - Saved models
- `scripts/` - Monitoring and utility scripts
- `environment.yml` - Conda environment for Azure ML
- `deployment.yml` - Azure ML deployment spec
- `Dockerfile` - Local/Docker deployment
- `k8s/` - Kubernetes manifests
- `iac/` - Infrastructure-as-code (Azure Bicep)

## MLOps Best Practices

- Version control for code and data
- Automated environment management
- Reproducible deployments
- Monitoring and alerting for model drift
- Infrastructure-as-code for cloud resources

## Production MLOps Roadmap

### Phase 1: Azure ML Deployment ✅
1. **Model Registration & Versioning**:
   ```powershell
   az ml model create --name fraud-detector --version 1 --path models/run_local/model.joblib
   ```

2. **Managed Online Endpoint Deployment**:
   ```powershell
   az ml online-endpoint create --file azureml/endpoint.yml
   az ml online-deployment create --file deployment.yml --resource-group mlops-rg --workspace-name scotia-mlops-ws
   ```

### Phase 2: Monitoring & Management
1. **Application Insights Integration**:
   - Enable monitoring in Azure ML workspace
   - Configure custom metrics for prediction accuracy
   - Set up alerts for latency > 2s or error rate > 5%

2. **Data & Model Drift Detection**:
   ```powershell
   python scripts/drift_monitor.py --baseline-data data/raw/txs.csv --new-data <incoming_data>
   ```

3. **Performance Monitoring Dashboard**:
   - Track prediction latency, throughput, and accuracy
   - Monitor resource utilization (CPU, memory)
   - Alert on model performance degradation

### Phase 3: Scaling & High Availability
1. **Auto-scaling Configuration**:
   ```yaml
   # In deployment.yml
   scale_settings:
     type: target_utilization
     min_instances: 2
     max_instances: 10
     target_utilization_percentage: 70
   ```

2. **Multi-region Deployment**:
   - Deploy endpoints in multiple Azure regions
   - Use Azure Traffic Manager for load balancing
   - Configure disaster recovery procedures

3. **API Gateway Integration**:
   - Deploy behind Azure API Management
   - Enable authentication, rate limiting, and caching
   - Implement request/response transformation

### Phase 4: CI/CD & Automation
1. **Automated Training Pipeline** (see `.azure-pipelines/training-pipeline.yml`)
2. **Continuous Deployment** (see `.github/workflows/deploy.yml`)
3. **Model Validation & Testing**:
   - Automated model performance testing
   - A/B testing for model versions
   - Rollback capabilities

### Phase 5: Security & Compliance
1. **Identity & Access Management**:
   - Use managed identities for Azure resources
   - Implement RBAC for model access
   - Enable audit logging

2. **Data Protection**:
   - Encrypt data at rest and in transit
   - Implement data lineage tracking
   - GDPR compliance for model explanations

### Phase 6: Cost Optimization
1. **Resource Management**:
   - Use spot instances for training workloads
   - Implement auto-shutdown for dev environments
   - Monitor and optimize compute costs

---

## Quick Commands Reference

### Local Development
```powershell
# Start local API
uvicorn src.serve:app --host 127.0.0.1 --port 8080

# Test endpoint
Invoke-RestMethod -Uri 'http://127.0.0.1:8080/predict' -Method POST -ContentType 'application/json' -Body '{"features": {"amount": 100, "hour_of_day": 14, "avg_monthly_spend": 500, "customer_tenure_days": 365, "num_prev_tx_24h": 5}}'

# Docker deployment
docker build -t fraud-api:latest .
docker run -p 8080:8080 fraud-api:latest
```

### Azure Deployment
```powershell
# Deploy to Azure ML
az ml online-deployment update --name fraud-deploy --endpoint-name fraud-endpoint --file deployment.yml --resource-group mlops-rg --workspace-name scotia-mlops-ws

# Monitor deployment
az ml online-endpoint show --name fraud-endpoint --resource-group mlops-rg --workspace-name scotia-mlops-ws

# Test Azure endpoint
az ml online-endpoint invoke --name fraud-endpoint --request-file test_data.json
```

## Automated Retraining and Deployment

This project includes a scheduled GitHub Actions workflow (`.github/workflows/retrain-and-deploy.yml`) that retrains the fraud detection model, registers it in Azure ML, and redeploys it to the managed endpoint.

**How it works:**
- Runs every Monday at 05:00 UTC (or manually via GitHub Actions > Run workflow)
- Retrains the model using `src/train.py` and the latest features data
- Registers the new model in Azure ML workspace
- Updates the endpoint deployment with the new model

**Customizing:**
- Change the schedule by editing the `cron` value in the workflow YAML
- Update training data path or script arguments as needed
- Monitor workflow runs and logs in the GitHub Actions tab

**Manual trigger:**
- Go to GitHub Actions > Retrain and Deploy Model > Run workflow

**Requirements:**
- Azure credentials must be set in repository secrets as `AZURE_CREDENTIALS`
- Training script must output model to `models/run_local/model.joblib`
- Deployment configuration is read from `deployment.yml`

---

For questions or contributions, please contact the project maintainer.
