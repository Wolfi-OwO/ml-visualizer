// Core infrastructure resources: Container Registry, Storage, etc.

@description('Environment name')
param environment string

@description('Azure region')
param location string

@description('Project name')
param projectName string

@description('Container Registry SKU')
param acrSku string

// Container Registry
resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: replace('${projectName}${environment}acr', '-', '')
  location: location
  sku: {
    name: acrSku
  }
  properties: {
    adminUserEnabled: true
    publicNetworkAccess: 'Enabled'
    networkRuleBypassOptions: 'AzureServices'
    zoneRedundancy: environment == 'production' ? 'Enabled' : 'Disabled'
  }
  tags: {
    Environment: environment
    Project: projectName
  }
}

// Log Analytics Workspace for container logs
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: '${projectName}-${environment}-logs'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: environment == 'production' ? 90 : 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
  tags: {
    Environment: environment
    Project: projectName
  }
}

// Outputs
output acrName string = acr.name
output acrLoginServer string = acr.properties.loginServer
output acrId string = acr.id
output logAnalyticsWorkspaceId string = logAnalytics.id
output logAnalyticsWorkspaceName string = logAnalytics.name
