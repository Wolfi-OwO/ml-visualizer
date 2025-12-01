// Monitoring resources: Application Insights, Alerts, Dashboards

@description('Environment name')
param environment string

@description('Azure region')
param location string

@description('Project name')
param projectName string

@description('App Service resource ID')
param appServiceId string

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${projectName}-${environment}-insights'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    RetentionInDays: environment == 'production' ? 90 : 30
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
  tags: {
    Environment: environment
    Project: projectName
  }
}

// Alert: High CPU usage
resource cpuAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: '${projectName}-${environment}-cpu-alert'
  location: 'global'
  properties: {
    description: 'Alert when CPU usage is high'
    severity: 2
    enabled: true
    scopes: [
      appServiceId
    ]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'HighCPU'
          metricName: 'CpuPercentage'
          operator: 'GreaterThan'
          threshold: 80
          timeAggregation: 'Average'
        }
      ]
    }
  }
  tags: {
    Environment: environment
    Project: projectName
  }
}

// Alert: High memory usage
resource memoryAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: '${projectName}-${environment}-memory-alert'
  location: 'global'
  properties: {
    description: 'Alert when memory usage is high'
    severity: 2
    enabled: true
    scopes: [
      appServiceId
    ]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'HighMemory'
          metricName: 'MemoryPercentage'
          operator: 'GreaterThan'
          threshold: 85
          timeAggregation: 'Average'
        }
      ]
    }
  }
  tags: {
    Environment: environment
    Project: projectName
  }
}

// Alert: HTTP 5xx errors
resource errorAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: '${projectName}-${environment}-error-alert'
  location: 'global'
  properties: {
    description: 'Alert when HTTP 5xx errors occur'
    severity: 1
    enabled: true
    scopes: [
      appServiceId
    ]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'HTTP5xxErrors'
          metricName: 'Http5xx'
          operator: 'GreaterThan'
          threshold: 10
          timeAggregation: 'Total'
        }
      ]
    }
  }
  tags: {
    Environment: environment
    Project: projectName
  }
}

// Alert: Response time
resource responseTimeAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: '${projectName}-${environment}-response-alert'
  location: 'global'
  properties: {
    description: 'Alert when response time is slow'
    severity: 3
    enabled: environment == 'production'
    scopes: [
      appServiceId
    ]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'SlowResponse'
          metricName: 'AverageResponseTime'
          operator: 'GreaterThan'
          threshold: 5
          timeAggregation: 'Average'
        }
      ]
    }
  }
  tags: {
    Environment: environment
    Project: projectName
  }
}

// Outputs
output appInsightsId string = appInsights.id
output appInsightsName string = appInsights.name
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
output appInsightsConnectionString string = appInsights.properties.ConnectionString
