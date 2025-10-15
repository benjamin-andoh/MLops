# Project Structure

## Overview

This document describes the organized structure of the Fraud Detection MLOps Pipeline project.

## Directory Tree

```
MLops/
│
├── .github/                          # GitHub Actions workflows
│   └── workflows/
│       ├── ci.yml                    # Continuous Integration pipeline
│       ├── deploy.yml                # Main deployment pipeline
│       ├── drift-monitor.yml         # Daily drift monitoring
│       └── retrain-and-deploy.yml    # Weekly automated retraining
│
├── data/                             # Data storage
│   ├── raw/                          # Raw input data
│   │   ├── txs.csv                   # Transaction records
│   │   └── txs_meta.json             # Transaction metadata
│   └── features/                     # Processed features (generated)
│
├── docs/                             # Documentation
│   ├── ADVANCED_MONITORING.md        # Monitoring setup & KQL queries
│   ├── CANARY_DEPLOYMENT.md          # Canary deployment guide
│   ├── MLOPS_SUMMARY.md              # Comprehensive MLOps pipeline overview
│   └── PROJECT_STRUCTURE.md          # This file
│
├── iac/                              # Infrastructure as Code
│   └── azure_bicep_example.bicep     # Azure Bicep template for resources
│
├── k8s/                              # Kubernetes configurations
│   └── deployment.yaml               # K8s deployment manifest
│
├── models/                           # Model artifacts
│   └── run_local/                    # Local model storage
│       └── model.joblib              # Trained scikit-learn model
│
├── scripts/                          # Utility scripts
│   └── drift_monitor.py              # Data drift detection script
│
├── src/                              # Source code
│   ├── features.py                   # Feature engineering
│   ├── generate_data.py              # Synthetic data generation
│   ├── score.py                      # Azure ML endpoint scoring script
│   ├── serve.py                      # FastAPI local serving
│   └── train.py                      # Model training script
│
├── tests/                            # Unit & integration tests
│   ├── conftest.py                   # Pytest configuration
│   ├── test_api.py                   # API endpoint tests
│   └── test_features.py              # Feature engineering tests
│
├── .gitignore                        # Git ignore rules
├── canary-deployment.yml             # Azure ML canary deployment config
├── deployment.yml                    # Azure ML main deployment config
├── deploy_to_azure.ps1               # PowerShell deployment script
├── Dockerfile                        # Container image definition
├── environment.yml                   # Conda environment specification
├── Makefile                          # Build automation
├── quick_local_test.py               # Quick local model test
├── README.md                         # Project overview
├── requirements.txt                  # Python dependencies
├── test_data.json                    # Sample test data for endpoint
└── test_endpoint.py                  # Endpoint testing script
```

## Key Components

### 🔄 CI/CD Pipelines (.github/workflows/)

- **ci.yml**: Runs tests, linting, and security checks on every push
- **deploy.yml**: Full deployment pipeline with smoke tests
- **retrain-and-deploy.yml**: Scheduled weekly retraining (Monday 05:00 UTC)
- **drift-monitor.yml**: Daily drift detection (06:00 UTC)

### 📊 Data Management (data/)

- **raw/**: Original transaction data
- **features/**: Generated feature sets (gitignored for large files)

### 📚 Documentation (docs/)

Comprehensive guides covering:

- MLOps pipeline architecture and workflow
- Advanced monitoring with Application Insights
- Canary deployment strategy
- Project structure and organization

### 🏗️ Infrastructure (iac/, k8s/)

- **iac/**: Azure Bicep templates for resource provisioning
- **k8s/**: Kubernetes deployment manifests (alternative to Azure ML)

### 🤖 Model Artifacts (models/)

- Trained model files (joblib format)
- Version controlled in Azure ML Model Registry
- Local copies stored for quick testing

### 🔧 Scripts (scripts/)

- **drift_monitor.py**: KS-test based drift detection
- Executed by GitHub Actions on schedule

### 💻 Source Code (src/)

- **features.py**: Feature engineering pipeline
- **generate_data.py**: Synthetic data generation for testing
- **score.py**: Azure ML endpoint scoring logic with Application Insights
- **serve.py**: FastAPI local development server
- **train.py**: Model training with metric logging

### ✅ Tests (tests/)

- **conftest.py**: Shared pytest fixtures
- **test_api.py**: API endpoint integration tests
- **test_features.py**: Feature engineering unit tests

### 📋 Configuration Files (root)

- **canary-deployment.yml**: Canary rollout configuration
- **deployment.yml**: Main Azure ML deployment config
- **environment.yml**: Conda environment (Python 3.10, Azure ML-compatible)
- **requirements.txt**: Python dependencies (matches environment.yml)
- **Dockerfile**: Container image for deployment
- **Makefile**: Automation for common tasks

### 🧪 Testing Utilities (root)

- **test_data.json**: Sample input for endpoint validation
- **test_endpoint.py**: Script to test deployed endpoint
- **quick_local_test.py**: Quick local model validation

## File Purpose Guide

| File/Directory            | Purpose                    | When to Modify                                       |
| ------------------------- | -------------------------- | ---------------------------------------------------- |
| `src/train.py`            | Model training logic       | When changing model architecture or training process |
| `src/score.py`            | Azure ML endpoint scoring  | When changing prediction logic or logging            |
| `src/features.py`         | Feature engineering        | When adding/modifying features                       |
| `deployment.yml`          | Azure ML deployment config | When changing instance type, scaling, or environment |
| `environment.yml`         | Conda dependencies         | When adding/updating Python packages                 |
| `.github/workflows/*.yml` | CI/CD pipelines            | When changing deployment process or schedules        |
| `tests/*.py`              | Unit & integration tests   | When adding new features or fixing bugs              |
| `docs/*.md`               | Documentation              | When updating processes or adding new guides         |

## Environment Configuration

### Python Environment

- **Version**: Python 3.10
- **Package Manager**: Conda (Azure ML) / pip (local)
- **Key Dependencies**:
  - scikit-learn 1.2.2
  - numpy 1.23.5
  - pandas 1.5.3
  - FastAPI, uvicorn (local serving)
  - opencensus-ext-azure (monitoring)

### Azure Resources

- **Workspace**: `mlops-scotia-ws2`
- **Endpoint**: `scotia-fraud-detection-endpoint`
- **Deployment**: `fraud-deployment`
- **Model**: `fraud-detection-model:2`
- **Instance**: `Standard_DS2_v2`

## Deployment Architecture

```
┌─────────────────┐
│  GitHub Repo    │
│  (feature/      │
│   build-ci-     │
│   pipeline)     │
└────────┬────────┘
         │
         ├─ Push/PR Trigger
         ↓
┌─────────────────────────────────────┐
│      GitHub Actions                 │
│  ┌─────────────────────────────┐   │
│  │ CI Pipeline                 │   │
│  │ - Test (pytest)             │   │
│  │ - Lint (flake8)             │   │
│  │ - Security Scan             │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ Deploy Pipeline             │   │
│  │ - Build Docker Image        │   │
│  │ - Push to ACR               │   │
│  │ - Deploy to Azure ML        │   │
│  │ - Smoke Test Endpoint       │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│      Azure ML Workspace             │
│  ┌─────────────────────────────┐   │
│  │ Model Registry              │   │
│  │ - fraud-detection-model:2   │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │ Managed Online Endpoint     │   │
│  │ - scotia-fraud-detection-   │   │
│  │   endpoint                  │   │
│  │ - fraud-deployment (100%)   │   │
│  │ - Standard_DS2_v2          │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│   Application Insights              │
│   - Request/Response Logging        │
│   - Performance Metrics             │
│   - Error Tracking                  │
│   - Custom Events                   │
└─────────────────────────────────────┘
```

## Monitoring & Observability

### Application Insights Integration

- **Logging**: All predictions logged with input/output
- **Metrics**: Request latency, throughput, error rates
- **Alerts**: Configured for high error rates, drift detection
- **Dashboards**: KQL queries for visualization

### Drift Monitoring

- **Schedule**: Daily at 06:00 UTC
- **Method**: Kolmogorov-Smirnov test
- **Threshold**: p-value < 0.1
- **Action**: Alert triggers retraining pipeline

## Best Practices

### 1. Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/your-feature

# 2. Make changes and test locally
python -m pytest tests/
python quick_local_test.py

# 3. Commit and push
git add .
git commit -m "Description of changes"
git push origin feature/your-feature

# 4. Create PR - CI pipeline runs automatically
# 5. Merge to main - Deploy pipeline runs automatically
```

### 2. Testing

- **Unit tests**: Test individual functions in `tests/test_features.py`
- **Integration tests**: Test API endpoints in `tests/test_api.py`
- **Endpoint tests**: Use `test_endpoint.py` for deployed endpoint validation

### 3. Model Updates

```bash
# 1. Retrain model locally
python src/train.py --features data/features/features.csv --output_dir models/run_local/

# 2. Test locally
python quick_local_test.py

# 3. Register in Azure ML (via GitHub Actions or manual)
az ml model create --name fraud-detection-model --path models/run_local/model.joblib --version 3

# 4. Update deployment.yml with new version
# 5. Deploy via GitHub Actions
```

### 4. Monitoring Queries

See `docs/ADVANCED_MONITORING.md` for comprehensive KQL queries for:

- Prediction distribution
- Response time analysis
- Error rate tracking
- Drift detection alerts

## Cleanup Completed

### Removed Redundant Files/Directories

✅ `sample.json` - Redundant with `test_data.json`
✅ `environment/conda.yml` - Redundant with root `environment.yml`
✅ `app/model/` - Redundant with `models/run_local/`
✅ `.azure-pipelines/` - Using GitHub Actions instead
✅ `azureml/endpoint.yml` - Using `deployment.yml` instead

### Organized Structure

✅ All deployment configs at root level
✅ Documentation consolidated in `docs/`
✅ Source code in `src/`
✅ Tests in `tests/`
✅ Scripts in `scripts/`
✅ Data in `data/`
✅ Models in `models/`

## Quick Reference Commands

### Local Development

```bash
# Activate environment
conda env create -f environment.yml
conda activate fraud-detection

# Run tests
python -m pytest tests/ -v

# Start local server
python src/serve.py

# Test local endpoint
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d @test_data.json
```

### Azure ML Deployment

```bash
# Deploy using PowerShell script
.\deploy_to_azure.ps1

# Or manually
az ml online-endpoint create --file deployment.yml
az ml online-deployment create --file deployment.yml
az ml online-endpoint update --name scotia-fraud-detection-endpoint --traffic "fraud-deployment=100"

# Test endpoint
python test_endpoint.py
```

### Monitoring

```bash
# Check deployment logs
az ml online-deployment get-logs --name fraud-deployment --endpoint-name scotia-fraud-detection-endpoint

# View Application Insights
# Navigate to Azure Portal → Application Insights → Logs
# Use queries from docs/ADVANCED_MONITORING.md
```

## Support

For detailed guides, see:

- **MLOps Overview**: `docs/MLOPS_SUMMARY.md`
- **Monitoring Setup**: `docs/ADVANCED_MONITORING.md`
- **Canary Deployments**: `docs/CANARY_DEPLOYMENT.md`
- **Main README**: `README.md`

---

**Last Updated**: January 2025  
**Project Status**: Production-Ready ✅
