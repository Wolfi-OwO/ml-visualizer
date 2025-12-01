// App Service resources with auto-scaling

@description('Environment name')
param environment string

@description('Azure region')
param location string

@description('Project name')
param projectName string

@description('App Service SKU')
param appServiceSku object

@description('Container Registry name')
param containerRegistryName string

@description('Container Registry URL')
param containerRegistryUrl string

// App Service Plan with auto-scaling
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${projectName}-${environment}-plan'
  location: location
  kind: 'linux'
  properties: {
    reserved: true
    zoneRedundant: environment == 'production'
  }
  sku: {
    name: appServiceSku.name
    tier: appServiceSku.tier
    capacity: appServiceSku.capacity
  }
  tags: {
    Environment: environment
    Project: projectName
  }
}

// Auto-scaling rules
resource autoScaleSettings 'Microsoft.Insights/autoscalesettings@2022-10-01' = {
  name: '${projectName}-${environment}-autoscale'
  location: location
  properties: {
    enabled: true
    targetResourceUri: appServicePlan.id
    profiles: [
      {
        name: 'Auto scale condition'
        capacity: {
          minimum: string(appServiceSku.capacity)
          maximum: environment == 'production' ? '10' : environment == 'staging' ? '5' : '3'
          default: string(appServiceSku.capacity)
        }
        rules: [
          {
            metricTrigger: {
              metricName: 'CpuPercentage'
              metricResourceUri: appServicePlan.id
              timeGrain: 'PT1M'
              statistic: 'Average'
              timeWindow: 'PT5M'
              timeAggregation: 'Average'
              operator: 'GreaterThan'
              threshold: 70
            }
            scaleAction: {
              direction: 'Increase'
              type: 'ChangeCount'
              value: '1'
              cooldown: 'PT5M'
            }
          }
          {
            metricTrigger: {
              metricName: 'CpuPercentage'
              metricResourceUri: appServicePlan.id
              timeGrain: 'PT1M'
              statistic: 'Average'
              timeWindow: 'PT10M'
              timeAggregation: 'Average'
              operator: 'LessThan'
              threshold: 30
            }
            scaleAction: {
              direction: 'Decrease'
              type: 'ChangeCount'
              value: '1'
              cooldown: 'PT10M'
            }
          }
          {
            metricTrigger: {
              metricName: 'MemoryPercentage'
              metricResourceUri: appServicePlan.id
              timeGrain: 'PT1M'
              statistic: 'Average'
              timeWindow: 'PT5M'
              timeAggregation: 'Average'
              operator: 'GreaterThan'
              threshold: 80
            }
            scaleAction: {
              direction: 'Increase'
              type: 'ChangeCount'
              value: '1'
              cooldown: 'PT5M'
            }
          }
        ]
      }
    ]
  }
  tags: {
    Environment: environment
    Project: projectName
  }
}

// Web App
resource webApp 'Microsoft.Web/sites@2023-01-01' = {
  name: '${projectName}-${environment}'
  location: location
  kind: 'app,linux,container'
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    clientAffinityEnabled: false
    siteConfig: {
      linuxFxVersion: 'DOCKER|${containerRegistryUrl}/${projectName}:latest'
      alwaysOn: environment != 'testing'
      http20Enabled: true
      minTlsVersion: '1.2'
      ftpsState: 'Disabled'
      healthCheckPath: '/_stcore/health'
      appSettings: [
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'false'
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_URL'
          value: 'https://${containerRegistryUrl}'
        }
        {
          name: 'DOCKER_ENABLE_CI'
          value: 'true'
        }
        {
          name: 'ENVIRONMENT_NAME'
          value: environment
        }
        {
          name: 'WEBSITES_PORT'
          value: '8501'
        }
      ]
    }
  }
  tags: {
    Environment: environment
    Project: projectName
  }
}

// Deployment slot for production (blue-green deployment)
resource productionSlot 'Microsoft.Web/sites/slots@2023-01-01' = if (environment == 'production') {
  parent: webApp
  name: 'staging'
  location: location
  kind: 'app,linux,container'
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'DOCKER|${containerRegistryUrl}/${projectName}:latest'
      alwaysOn: true
      healthCheckPath: '/_stcore/health'
    }
  }
}

// Outputs
output appServiceId string = webApp.id
output appServiceName string = webApp.name
output appServiceUrl string = 'https://${webApp.properties.defaultHostName}'
output appServicePlanId string = appServicePlan.id
