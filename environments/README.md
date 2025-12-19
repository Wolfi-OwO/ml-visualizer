# Environment Management Guide

This document outlines the multi-environment deployment strategy for the DSAI Webapp application.

## Environment Architecture

### Testing Environment Details

- **Purpose**: Automatic deployment for all feature branches
- **Trigger**: Push to any branch (except main)
- **URL Pattern**: `https://${AZURE_WEBAPP_NAME}-testing.azurewebsites.net`
- **Deployment**: Automatic
- **Health Checks**: Basic connectivity
- **Retention**: Temporary (auto-stopped when branch is deleted)

### Staging Environment Details

- **Purpose**: Pre-production validation and acceptance testing
- **Trigger**: Manual deployment from `develop` or `main` branches
- **URL Pattern**: `https://${AZURE_WEBAPP_NAME}-staging.azurewebsites.net`
- **Deployment**: Manual (requires approval)
- **Health Checks**: Comprehensive (connectivity + response time)
- **Retention**: Persistent

### Production Environment Details

- **Purpose**: Live production system
- **Trigger**: Manual deployment from `main` branch only
- **URL Pattern**: `https://${AZURE_WEBAPP_NAME}.azurewebsites.net`
- **Deployment**: Manual (requires approval)
- **Health Checks**: Critical (connectivity + response time + performance)
- **Retention**: Persistent + backup metadata
- **Rollback**: Emergency and specific version rollback available

## Deployment Flow

```text
Feature Branch → Testing Environment (Auto)
                ↓
Develop Branch → Staging Environment (Manual)
                ↓
Main Branch → Production Environment (Manual)
```

## Azure Resource Requirements

Each environment requires its own Azure App Service:

### Testing Environment Setup

```bash
# Create testing app service
az webapp create \
  --resource-group ${AZURE_RESOURCE_GROUP} \
  --plan ${AZURE_APP_SERVICE_PLAN} \
  --name ${AZURE_WEBAPP_NAME}-testing \
  --deployment-container-image-name ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:latest
```

### Staging Environment Setup

```bash
# Create staging app service
az webapp create \
  --resource-group ${AZURE_RESOURCE_GROUP} \
  --plan ${AZURE_APP_SERVICE_PLAN} \
  --name ${AZURE_WEBAPP_NAME}-staging \
  --deployment-container-image-name ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:latest
```

### Production Environment Setup

```bash
# Production app service (already exists)
# Uses: ${AZURE_WEBAPP_NAME}
```

## Environment Variables

### Required GitLab CI/CD Variables

- `AZURE_WEBAPP_NAME`: Base name for production app service
- `AZURE_RESOURCE_GROUP`: Resource group containing all environments
- `AZURE_APP_SERVICE_PLAN`: App service plan for all environments
- `ACR_NAME`: Azure Container Registry name
- `AZURE_SUBSCRIPTION_ID`: Azure subscription ID
- `AZURE_CLIENT_ID`: Service principal client ID
- `AZURE_CLIENT_SECRET`: Service principal client secret
- `AZURE_TENANT_ID`: Azure tenant ID

### Auto-Generated Variables

- `TESTING_WEBAPP_NAME`: `${AZURE_WEBAPP_NAME}-testing`
- `STAGING_WEBAPP_NAME`: `${AZURE_WEBAPP_NAME}-staging`
- `PRODUCTION_WEBAPP_NAME`: `${AZURE_WEBAPP_NAME}`

## Deployment Strategies

### 1. Feature Development

- Create feature branch
- Push commits → Triggers automatic testing deployment
- Test functionality on testing environment
- Create merge request to `develop`

### 2. Staging Validation

- Merge to `develop` branch
- Manually trigger staging deployment via GitLab UI
- Perform acceptance testing on staging
- Create merge request to `main`

### 3. Production Release

- Merge to `main` branch
- Manually trigger production deployment via GitLab UI
- Monitor health checks and performance
- Emergency rollback available if needed

## Health Check Details

### Testing Environment Checks

- Basic HTTP 200 response check
- 30 attempts with 10-second intervals (5 minutes total)
- Failure blocks pipeline

### Staging Environment Checks

- HTTP 200 response check
- Response time validation
- 30 attempts with 10-second intervals
- Enhanced logging for debugging

### Production Environment Checks

- HTTP 200 response check
- Response time validation (< 5 seconds)
- 60 attempts with 10-second intervals (10 minutes)
- Critical failure triggers auto-rollback consideration
- Performance monitoring

## Rollback Procedures

### Emergency Rollback (Production)

1. Go to GitLab: CI/CD → Pipelines
2. Click "Play" on `rollback:production:emergency`
3. Automatically rolls back to second-latest stable version
4. No variables required

### Specific Version Rollback (Production)

1. Go to GitLab: CI/CD → Pipelines
2. Click "Play" on `rollback:production:specific`
3. Set variable: `ROLLBACK_VERSION=1.2.3`
4. Rolls back to specified version

### Available Versions

- Run `release:list-versions` job to see all available versions
- Versions are semantic versions (1.0.0, 1.1.0, etc.)
- Container registry maintains version history

## Security Considerations

### Environment Isolation

- Each environment uses separate Azure App Services
- No shared databases or storage between environments
- Independent scaling and configuration

### Access Control

- Production deployments require manual approval
- Protected branches (main) restrict who can trigger production
- Service principal has minimal required permissions

### Data Protection

- No production data in testing/staging environments
- Mock data or anonymized datasets only
- Secrets managed through GitLab CI/CD variables

## Monitoring and Logging

### Deployment Reports

- Each environment generates deployment reports
- Health check results logged
- Performance metrics captured
- Artifacts stored for troubleshooting

### Environment URLs

- Testing: Available in job logs and artifacts
- Staging: Available in GitLab environments tab
- Production: Available in GitLab environments tab

### Alert Channels

- Failed deployments trigger GitLab notifications
- Health check failures logged in deployment reports
- Manual intervention required for production issues

## Troubleshooting

### Common Issues

#### Testing Environment Not Accessible

1. Check if testing app service exists in Azure
2. Verify container image deployment
3. Check health check logs in deployment artifacts
4. Restart testing app service if needed

#### Staging Deployment Fails

1. Verify develop/main branch permissions
2. Check Azure resource group permissions
3. Validate container image exists in registry
4. Review staging deployment report artifacts

#### Production Deployment Blocked

1. Ensure manual approval given
2. Check all health checks pass
3. Verify production app service is running
4. Review production deployment report

#### Rollback Failures

1. Verify target version exists in container registry
2. Check Azure App Service permissions
3. Review rollback report artifacts
4. Manual Azure portal intervention if needed

### Support Commands

#### List Available Versions

```bash
az acr repository show-tags \
  --name ${ACR_NAME} \
  --repository ml-visualizer \
  --orderby time_desc \
  --output table
```

#### Check App Service Status

```bash
az webapp show \
  --name ${WEBAPP_NAME} \
  --resource-group ${AZURE_RESOURCE_GROUP} \
  --query "state" \
  --output tsv
```

#### Manual App Service Restart

```bash
az webapp restart \
  --name ${WEBAPP_NAME} \
  --resource-group ${AZURE_RESOURCE_GROUP}
```

## Best Practices

### Branch Strategy

- `main`: Production releases only
- `develop`: Integration branch for staging
- `feature/*`: Individual features for testing
- `hotfix/*`: Critical production fixes

### Version Management

- Use semantic versioning (1.0.0, 1.1.0, 2.0.0)
- Update VERSION file for releases
- Tag important releases in Git
- Maintain changelog for major versions

### Testing Strategy

- Unit tests run on all branches
- Integration tests on staging
- Smoke tests on all environments
- Performance tests before production

### Deployment Timing

- Testing: Continuous (on push)
- Staging: Daily integration
- Production: Weekly releases (or as needed)
- Hotfixes: Emergency deployment to production

### Monitoring

- Check environment health daily
- Review deployment reports weekly
- Monitor resource usage monthly
- Update dependencies quarterly
