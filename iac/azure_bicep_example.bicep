// File: iac/azure_bicep_example.bicep
// Minimal example (edit for your environment). Deploy with: az deployment group create -g <rg> -f ./azure_bicep_example.bicep
param workspaceName string = 'ml-workspace-demo'
param location string = resourceGroup().location
resource storage 'Microsoft.Storage/storageAccounts@2021-04-01' = {
  name: 'mlstorage${uniqueString(resourceGroup().id)}'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
}
resource acr 'Microsoft.ContainerRegistry/registries@2021-09-01' = {
  name: 'acr${uniqueString(resourceGroup().id)}'
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {}
}
// Note: Azure ML workspace resource schema is available - include as needed for production
output storageAccount string = storage.name
output acrName string = acr.name
