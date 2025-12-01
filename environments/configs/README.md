# Environment Configuration Guide

Complete setup and configuration guide for multi-environment deployment.

## Configuration Overview

```yaml
environments:
  testing:
    url: https://ml-visualizer-testing.azurewebsites.net
    trigger: automatic (on commits)
  staging:
    url: https://ml-visualizer-staging.azurewebsites.net
    trigger: manual (develop branch)
  production:
    url: https://ml-visualizer.azurewebsites.net
    trigger: manual (main branch)
```

## Setup Process

### 1. Environment Setup

Run the automated setup script:

```bash
./setup-production-environments.sh
```

This script will:

1. Create Azure resource groups
2. Set up App Service plans and web apps
3. Configure container registry
4. Generate GitLab CI/CD variables

### 2. GitLab CI/CD Variables

Navigate to GitLab project → Settings → CI/CD → Variables

#### Required Variables (Protected)

- `AZURE_SUBSCRIPTION_ID`: Azure subscription ID
- `AZURE_CLIENT_ID`: Service principal client ID
- `AZURE_CLIENT_SECRET`: Service principal secret
- `AZURE_TENANT_ID`: Azure AD tenant ID
- `AZURE_CONTAINER_REGISTRY`: Registry name (without .azurecr.io)
- `AZURE_RESOURCE_GROUP`: Main resource group name
- `AZURE_WEBAPP_NAME`: Base app service name

#### Optional Variables

- `ROLLBACK_VERSION`: Specific version for rollback operations
- `HEALTH_CHECK_TIMEOUT`: Health check timeout (default: 30s)

### Environment URLs

### Testing Environment

- **URL**: `https://${AZURE_WEBAPP_NAME}-testing.azurewebsites.net`
- **Purpose**: Automated testing and validation
- **Trigger**: Every commit to feature branches

### Staging Environment

- **URL**: `https://${AZURE_WEBAPP_NAME}-staging.azurewebsites.net`
- **Purpose**: Pre-production validation and user acceptance testing
- **Trigger**: Manual deployment from develop branch

### Production Environment

- **URL**: `https://${AZURE_WEBAPP_NAME}.azurewebsites.net`
- **Purpose**: Live production system
- **Trigger**: Manual deployment from main branch

## Deployment Workflow

### Feature Development

1. Create feature branch from `develop`
2. Commit triggers automatic testing environment deployment
3. Validate functionality in testing environment
4. Create merge request to `develop`

### Staging Release

1. Merge feature to `develop`
2. Manually trigger staging deployment from GitLab pipeline
3. Perform user acceptance testing
4. Create merge request to `main` if approved

### Production Release

1. Merge to `main` branch
2. Manually trigger production deployment
3. Monitor health checks and performance
4. Tag release version

## Rollback Procedures

### Emergency Rollback

1. Access GitLab CI/CD → Pipelines
2. Click "Run pipeline" on main branch
3. Set variable: `ROLLBACK_ENVIRONMENT` = `auto`
4. Click "Run pipeline" - automatically rolls back to last known good version

### Specific Version Rollback

1. Access GitLab CI/CD → Pipelines
2. Click "Run pipeline" on main branch
3. Set variables:
   - `ROLLBACK_ENVIRONMENT` = `specific`
   - `ROLLBACK_VERSION` = `target-version`
4. Click "Run pipeline"

## Security Configuration

### Branch Protection

- `main` branch: Protected, requires merge requests
- `develop` branch: Protected, requires merge requests
- Feature branches: Standard permissions

### Secret Management

- All sensitive variables stored in GitLab CI/CD variables
- Variables marked as "Protected" for main/develop branches only
- Secrets are masked in pipeline logs
- Service principal has minimal required permissions

### Access Control

- Service principal has minimal required permissions
- Separate resource groups for environment isolation
- Network access controls on App Services
- Container registry access restricted to CI/CD pipeline

## Monitoring & Alerting

### Health Checks

- Automated health checks on all environments
- SSL certificate expiration monitoring
- Response time validation
- Application content verification

### Logging

- Structured logging with environment identification
- Centralized log aggregation in Azure
- Pipeline execution logs in GitLab
- Health check execution logs

### Alerting Channels

- GitLab pipeline notifications
- Azure Monitor alerts for infrastructure issues
- Health check failure notifications
- SSL certificate expiration warnings

## Troubleshooting

### Common Issues

#### Environment Not Responding

1. Check app service status in Azure portal
2. Verify container image deployment
3. Check application logs in Azure
4. Run manual health check script
5. Verify network connectivity and DNS

#### Deployment Failures

1. Verify GitLab CI/CD variables are configured
2. Check service principal permissions
3. Validate Azure CLI authentication in pipeline
4. Review pipeline logs for specific error messages
5. Test container image locally

#### Performance Issues

1. Monitor response times in health checks
2. Check Azure App Service metrics
3. Review application resource usage
4. Analyze container logs for bottlenecks
5. Consider scaling up App Service plan
6. Validate database connections and performance

### Diagnostic Commands

#### Check Environment Status

```bash
# Run health check on all environments
./environments/scripts/health-check.sh all

# Check specific environment
./environments/scripts/health-check.sh production

# Validate SSL certificates
./environments/scripts/health-check.sh staging ssl-only
```

#### Container Registry Operations

```bash
# List all images in registry
az acr repository list --name $AZURE_CONTAINER_REGISTRY

# Check image tags
az acr repository show-tags --name $AZURE_CONTAINER_REGISTRY --repository ml-visualizer

# Clean up old images
az acr repository delete --name $AZURE_CONTAINER_REGISTRY --image ml-visualizer:old-tag
```

### Escalation Contacts

#### Technical Escalation

- **Primary**: Development Team Lead
- **Secondary**: DevOps Engineer
- **Email**: <tech-support@company.com>

#### Business Escalation

- **Primary**: Product Owner
- **Secondary**: Project Manager
- **Email**: <business-support@company.com>
