// Main Bicep template for ML Visualizer Infrastructure
// Deploys all resources needed for the application

targetScope = 'subscription'

@description('The environment name (testing, staging, production)')
@allowed([
  'testing'
  'staging'
  'production'
])
param environment string

@description('Azure region for all resources')
param location string = 'westeurope'

@description('Resource name prefix')
param projectName string = 'ml-visualizer'

@description('Container Registry SKU')
@allowed([
  'Basic'
  'Standard'
  'Premium'
])
param acrSku string = environment == 'production' ? 'Premium' : 'Standard'

@description('App Service Plan SKU')
param appServiceSku object = environment == 'production' ? {
  name: 'P1v3'
  tier: 'Premium'
  capacity: 2
} : environment == 'staging' ? {
  name: 'S1'
  tier: 'Standard'
  capacity: 1
} : {
  name: 'B2'
  tier: 'Basic'
  capacity: 1
}

// Create resource group
resource rg 'Microsoft.Resources/resourceGroups@2023-07-01' = {
  name: '${projectName}-${environment}-rg'
  location: location
  tags: {
    Environment: environment
    Project: projectName
    ManagedBy: 'Bicep'
  }
}

// Deploy core infrastructure
module coreInfra 'modules/core-infrastructure.bicep' = {
  scope: rg
  name: 'coreInfrastructure'
  params: {
    environment: environment
    location: location
    projectName: projectName
    acrSku: acrSku
  }
}

// Deploy app services
module appService 'modules/app-service.bicep' = {
  scope: rg
  name: 'appService'
  params: {
    environment: environment
    location: location
    projectName: projectName
    appServiceSku: appServiceSku
    containerRegistryName: coreInfra.outputs.acrName
    containerRegistryUrl: coreInfra.outputs.acrLoginServer
  }
}

// Deploy monitoring
module monitoring 'modules/monitoring.bicep' = {
  scope: rg
  name: 'monitoring'
  params: {
    environment: environment
    location: location
    projectName: projectName
    appServiceId: appService.outputs.appServiceId
  }
}

// Outputs
output resourceGroupName string = rg.name
output acrName string = coreInfra.outputs.acrName
output acrLoginServer string = coreInfra.outputs.acrLoginServer
output appServiceName string = appService.outputs.appServiceName
output appServiceUrl string = appService.outputs.appServiceUrl
output appInsightsInstrumentationKey string = monitoring.outputs.appInsightsInstrumentationKey
