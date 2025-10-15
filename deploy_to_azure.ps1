# Azure ML Deployment Script
# Run this script as Administrator in PowerShell

Write-Host "Starting Azure ML deployment process..." -ForegroundColor Green

# Step 1: Fix Azure CLI ML extension
Write-Host "Fixing Azure CLI ML extension..." -ForegroundColor Yellow
try {
    # Remove corrupted extension directory (requires admin rights)
    $mlExtPath = "$env:USERPROFILE\.azure\cliextensions\ml"
    if (Test-Path $mlExtPath) {
        Remove-Item $mlExtPath -Recurse -Force
        Write-Host "Removed corrupted ML extension" -ForegroundColor Green
    }
    
    # Reinstall ML extension
    az extension add --name ml --upgrade
    Write-Host "Reinstalled Azure ML extension" -ForegroundColor Green
} catch {
    Write-Host "Failed to fix ML extension. Please run as Administrator." -ForegroundColor Red
    exit 1
}

# Step 2: Register required resource providers
Write-Host "Registering Azure resource providers..." -ForegroundColor Yellow
az provider register --namespace Microsoft.MachineLearningServices
az provider register --namespace Microsoft.Storage
az provider register --namespace Microsoft.KeyVault
az provider register --namespace Microsoft.ContainerRegistry

# Step 3: Create Azure ML workspace
Write-Host "Creating Azure ML workspace..." -ForegroundColor Yellow
az ml workspace create `
    --name scotia-mlops-ws `
    --resource-group mlops-rg `
    --location eastus `
    --display-name "Scotia MLOps Workspace" `
    --description "MLOps workspace for fraud detection"

# Step 4: Register model
Write-Host "Registering fraud detection model..." -ForegroundColor Yellow
az ml model create `
    --name fraud-detector `
    --version 1 `
    --path models/run_local/model.joblib `
    --resource-group mlops-rg `
    --workspace-name scotia-mlops-ws `
    --description "Fraud detection model trained with scikit-learn"

# Step 5: Create online endpoint
Write-Host "Creating online endpoint..." -ForegroundColor Yellow
az ml online-endpoint create `
    --file azureml/endpoint.yml `
    --resource-group mlops-rg `
    --workspace-name scotia-mlops-ws

# Step 6: Deploy model to endpoint
Write-Host "Deploying model to endpoint..." -ForegroundColor Yellow
az ml online-deployment create `
    --file deployment.yml `
    --resource-group mlops-rg `
    --workspace-name scotia-mlops-ws

# Step 7: Set traffic to 100% for the deployment
Write-Host "Setting endpoint traffic..." -ForegroundColor Yellow
az ml online-endpoint update `
    --name fraud-endpoint `
    --traffic "fraud-deploy=100" `
    --resource-group mlops-rg `
    --workspace-name scotia-mlops-ws

# Step 8: Test the deployment
Write-Host "Testing the deployed endpoint..." -ForegroundColor Yellow
az ml online-endpoint invoke `
    --name fraud-endpoint `
    --request-file test_data.json `
    --resource-group mlops-rg `
    --workspace-name scotia-mlops-ws

Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host "Your fraud detection API is now live on Azure ML!" -ForegroundColor Cyan