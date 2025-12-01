# Deployment Checklist

Use this checklist to ensure all steps are completed when setting up your production-ready environment.

##  Pre-Deployment

### Local Setup
- [ ] Clone repository
- [ ] Install Docker and Docker Compose
- [ ] Install Azure CLI (`az --version`)
- [ ] Install Python 3.12+
- [ ] Test local development: `docker-compose -f docker-compose.dev.yml up`
- [ ] Verify app works at http://localhost:8501
- [ ] Run tests: `pytest tests/ -v`
- [ ] All tests passing

### Azure Prerequisites
- [ ] Azure subscription active
- [ ] Azure CLI logged in: `az login`
- [ ] Correct subscription selected: `az account show`
- [ ] Contributor permissions verified
- [ ] Decided on Azure region (e.g., westeurope)

### GitHub Prerequisites
- [ ] Repository created/cloned
- [ ] GitHub CLI installed (optional): `gh --version`
- [ ] GitHub account has admin access to repository
- [ ] Branches created: `develop`, `staging`, `main`

##  Infrastructure Deployment

### Testing Environment
- [ ] Deploy: `./infrastructure/deploy.sh testing westeurope`
- [ ] Deployment successful (check output)
- [ ] Resource group created: `ml-visualizer-testing-rg`
- [ ] Container registry accessible
- [ ] App Service created
- [ ] Application Insights configured
- [ ] Save outputs to safe location

### Staging Environment
- [ ] Deploy: `./infrastructure/deploy.sh staging westeurope`
- [ ] Deployment successful
- [ ] Resource group created: `ml-visualizer-staging-rg`
- [ ] All resources provisioned
- [ ] Save outputs

### Production Environment
- [ ] Deploy: `./infrastructure/deploy.sh production westeurope`
- [ ] Deployment successful
- [ ] Resource group created: `ml-visualizer-production-rg`
- [ ] All resources provisioned
- [ ] Production slot created
- [ ] Save outputs securely

### Verify Infrastructure
- [ ] List resource groups: `az group list -o table`
- [ ] Check testing resources: `az resource list --resource-group ml-visualizer-testing-rg -o table`
- [ ] Check staging resources: `az resource list --resource-group ml-visualizer-staging-rg -o table`
- [ ] Check production resources: `az resource list --resource-group ml-visualizer-production-rg -o table`
- [ ] Get ACR credentials: `az acr credential show --name <acr-name>`

##  GitHub Configuration

### Service Principal Setup
- [ ] Create service principal:
  ```bash
  az ad sp create-for-rbac --name "ml-visualizer-cicd" \
    --role contributor \
    --scopes /subscriptions/<sub-id> \
    --sdk-auth
  ```
- [ ] Save JSON output securely
- [ ] Verify service principal: `az ad sp list --display-name "ml-visualizer-cicd"`

### GitHub Secrets
- [ ] Go to GitHub: Settings → Secrets and variables → Actions
- [ ] Add `AZURE_CREDENTIALS` (service principal JSON)
- [ ] Add `ACR_USERNAME` (from ACR credentials)
- [ ] Add `ACR_PASSWORD` (from ACR credentials)
- [ ] Verify all secrets added: `gh secret list` (if using GitHub CLI)

### GitHub Environments
- [ ] Create environment: `testing`
- [ ] Create environment: `staging`
- [ ] Create environment: `production`
- [ ] Create environment: `production-approval` with required reviewers
- [ ] Add yourself/team as required reviewer for production-approval

### Update Workflow Files
- [ ] Edit `.github/workflows/deploy-testing.yml`
  - [ ] Update `AZURE_WEBAPP_NAME`
  - [ ] Update `ACR_NAME`
  - [ ] Update `RESOURCE_GROUP`
- [ ] Edit `.github/workflows/deploy-staging.yml`
  - [ ] Update `AZURE_WEBAPP_NAME`
  - [ ] Update `ACR_NAME`
  - [ ] Update `RESOURCE_GROUP`
- [ ] Edit `.github/workflows/deploy-production.yml`
  - [ ] Update `AZURE_WEBAPP_NAME`
  - [ ] Update `ACR_NAME`
  - [ ] Update `RESOURCE_GROUP`

##  CI/CD Pipeline Testing

### Test CI Pipeline
- [ ] Create test branch: `git checkout -b test-ci`
- [ ] Make small change: `echo "# Test" >> README.md`
- [ ] Commit and push: `git add . && git commit -m "test: CI" && git push origin test-ci`
- [ ] Go to GitHub Actions tab
- [ ] Verify CI workflow runs
- [ ] Check all jobs pass (test, security, docker-build)
- [ ] Review test results and coverage

### Test Testing Deployment
- [ ] Merge test branch to develop (or push directly to develop)
- [ ] `git checkout develop && git push origin develop`
- [ ] Go to GitHub Actions tab
- [ ] Verify deploy-testing workflow runs
- [ ] Check build succeeds
- [ ] Check image pushed to ACR
- [ ] Check deployment to App Service
- [ ] Check health check passes
- [ ] Visit testing URL and verify app works

### Test Staging Deployment
- [ ] Merge develop to staging: `git checkout staging && git merge develop && git push origin staging`
- [ ] Verify deploy-staging workflow runs
- [ ] Check all steps succeed
- [ ] Visit staging URL and verify app works
- [ ] Run smoke tests if configured

### Test Production Deployment
- [ ] Merge staging to main: `git checkout main && git merge staging && git push origin main`
- [ ] Verify deploy-production workflow starts
- [ ] **IMPORTANT**: Approve the deployment in GitHub Actions
- [ ] Verify deployment completes
- [ ] Check health endpoint: `curl https://ml-visualizer-prod.azurewebsites.net/_stcore/health`
- [ ] Visit production URL
- [ ] Test all pages/features
- [ ] Verify monitoring in Application Insights

##  Monitoring Setup

### Application Insights
- [ ] Open Azure Portal → Application Insights
- [ ] Find `ml-visualizer-testing-insights`
- [ ] Find `ml-visualizer-staging-insights`
- [ ] Find `ml-visualizer-production-insights`
- [ ] Verify data is flowing
- [ ] Test querying logs
- [ ] Set up custom dashboards (optional)

### Alerts Configuration
- [ ] Verify CPU alert created
- [ ] Verify Memory alert created
- [ ] Verify HTTP 5xx alert created
- [ ] Verify Response time alert created
- [ ] Test alert by generating load (optional)
- [ ] Add email notifications to alerts
- [ ] Add SMS notifications (optional)

### Log Analytics
- [ ] Open Log Analytics workspace
- [ ] Verify logs are being collected
- [ ] Test running queries
- [ ] Create saved queries for common scenarios
- [ ] Set up log retention policies

##  Security Hardening

### App Service
- [ ] Verify HTTPS only: `az webapp show --name <app> --resource-group <rg> --query httpsOnly`
- [ ] Verify minimum TLS 1.2
- [ ] Configure IP restrictions (optional)
- [ ] Enable managed identity (optional)
- [ ] Review security recommendations in Azure Portal

### Container Registry
- [ ] Verify admin user enabled (for CI/CD)
- [ ] Consider disabling admin user and using managed identity (advanced)
- [ ] Review access policies
- [ ] Enable vulnerability scanning

### Secrets Management
- [ ] Verify no secrets in code
- [ ] Verify no secrets in environment files
- [ ] All secrets in GitHub Secrets or Azure Key Vault
- [ ] Rotate ACR password regularly
- [ ] Set up Key Vault for additional secrets (optional)

##  Performance Tuning

### Auto-Scaling
- [ ] Verify auto-scale rules in Azure Portal
- [ ] Test scale out (generate load)
- [ ] Test scale in (remove load)
- [ ] Adjust thresholds if needed
- [ ] Set appropriate min/max instances

### App Service Plan
- [ ] Verify correct SKU for each environment
- [ ] Testing: B2 or S1
- [ ] Staging: S1 or P1v3
- [ ] Production: P1v3 or higher
- [ ] Enable Always On for staging and production

### Optimization
- [ ] Enable HTTP/2
- [ ] Configure health check path: `/_stcore/health`
- [ ] Set appropriate timeouts
- [ ] Review and optimize resource limits

##  Documentation & Training

### Update Documentation
- [ ] Review README.md
- [ ] Review DEPLOYMENT.md
- [ ] Add custom deployment notes (if any)
- [ ] Document any environment-specific configurations
- [ ] Update architecture diagrams (if needed)

### Team Training
- [ ] Share QUICK_REFERENCE.md with team
- [ ] Walk through deployment process
- [ ] Demonstrate rollback procedure
- [ ] Show monitoring dashboards
- [ ] Explain branch strategy
- [ ] Practice incident response

##  Post-Deployment

### Validation
- [ ] All environments accessible via HTTPS
- [ ] All pages load correctly
- [ ] Health checks passing
- [ ] Metrics appearing in Application Insights
- [ ] Logs flowing to Log Analytics
- [ ] Alerts configured and tested

### Backups
- [ ] Configure App Service backup (optional)
- [ ] Document backup/restore procedures
- [ ] Test restore process
- [ ] Set up regular backup schedule

### Cost Management
- [ ] Set up cost alerts in Azure
- [ ] Review resource costs: `az consumption usage list`
- [ ] Optimize resource allocation
- [ ] Stop non-production environments when not in use (optional)
- [ ] Set up auto-shutdown for dev/test (optional)

### Maintenance Plan
- [ ] Schedule for dependency updates (monthly)
- [ ] Schedule for security patches (as needed)
- [ ] Schedule for certificate renewal (if using custom domains)
- [ ] Schedule for backup testing (quarterly)
- [ ] Schedule for disaster recovery drills (quarterly)

##  Final Checks

### Testing Environment
- [ ] URL works: https://ml-visualizer-testing.azurewebsites.net
- [ ] Health check: https://ml-visualizer-testing.azurewebsites.net/_stcore/health
- [ ] All pages accessible
- [ ] Deployment from develop branch works

### Staging Environment
- [ ] URL works: https://ml-visualizer-staging.azurewebsites.net
- [ ] Health check: https://ml-visualizer-staging.azurewebsites.net/_stcore/health
- [ ] All pages accessible
- [ ] Deployment from staging branch works

### Production Environment
- [ ] URL works: https://ml-visualizer-prod.azurewebsites.net
- [ ] Health check: https://ml-visualizer-prod.azurewebsites.net/_stcore/health
- [ ] All pages accessible
- [ ] Deployment from main branch works with approval
- [ ] Production slot works (if configured)

### CI/CD Pipeline
- [ ] CI runs on all pushes/PRs
- [ ] Tests execute and pass
- [ ] Security scanning completes
- [ ] Docker build succeeds
- [ ] Deployments work for all environments
- [ ] Rollback procedure tested

### Monitoring
- [ ] Application Insights collecting data
- [ ] Alerts firing correctly (test)
- [ ] Logs searchable in Log Analytics
- [ ] Dashboards showing metrics
- [ ] Health checks green

##  Sign-Off

- [ ] **Technical Lead Review**: _____________________ Date: _______
- [ ] **Security Review**: _____________________ Date: _______
- [ ] **DevOps Review**: _____________________ Date: _______
- [ ] **Final Approval**: _____________________ Date: _______

##  Congratulations!

Your production-ready ML Visualizer is now fully deployed and operational!

### Next Steps
1. Monitor the application for the first 24-48 hours
2. Review metrics and adjust scaling if needed
3. Set up custom domain (if required)
4. Configure SSL certificates (if using custom domain)
5. Share URLs with stakeholders
6. Begin normal development workflow

### Need Help?
- Review [DEPLOYMENT.md](DEPLOYMENT.md) for detailed procedures
- Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for common commands
- Review logs in Azure Portal
- Check Application Insights for issues

---

**Deployment Date**: ________________
**Deployed By**: ____________________
**Version**: 1.0.0


# ML Visualizer - Deployment Guide

Complete guide for deploying the ML Visualizer application to Azure with CI/CD pipelines.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Architecture Overview](#architecture-overview)
- [Quick Start](#quick-start)
- [Environment Setup](#environment-setup)
- [Azure Infrastructure Deployment](#azure-infrastructure-deployment)
- [CI/CD Pipeline Configuration](#cicd-pipeline-configuration)
- [Application Deployment](#application-deployment)
- [Scaling and Performance](#scaling-and-performance)
- [Monitoring and Alerts](#monitoring-and-alerts)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools

- **Azure CLI** (v2.50+): `az --version`
- **Docker** (v24+): `docker --version`
- **Git**: `git --version`
- **Azure Subscription**: Active Azure subscription with contributor access

### Optional Tools

- **kubectl**: For Kubernetes deployments (future)
- **Terraform**: Alternative to Bicep (if preferred)

### Azure Requirements

- Azure subscription
- Permissions to create:
  - Resource Groups
  - Container Registries
  - App Services
  - Application Insights
  - Log Analytics Workspaces

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Repository                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   develop    │  │   staging    │  │     main     │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
└─────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │
          ▼                  ▼                  ▼
    ┌─────────┐        ┌─────────┐       ┌─────────┐
    │ Testing │        │ Staging │       │  Prod   │
    │  CI/CD  │        │  CI/CD  │       │  CI/CD  │
    └────┬────┘        └────┬────┘       └────┬────┘
         │                  │                  │
         ▼                  ▼                  ▼
    ┌─────────────────────────────────────────────────┐
    │         Azure Container Registry (ACR)          │
    └─────────────────────────────────────────────────┘
         │                  │                  │
         ▼                  ▼                  ▼
    ┌─────────┐        ┌─────────┐       ┌─────────┐
    │ Testing │        │ Staging │       │  Prod   │
    │App Svc  │        │App Svc  │       │App Svc  │
    └─────────┘        └─────────┘       └─────────┘
         │                  │                  │
         └──────────────────┴──────────────────┘
                            │
                            ▼
                   ┌────────────────┐
                   │ App Insights   │
                   │  & Monitoring  │
                   └────────────────┘
```

### Environment Strategy

- **Testing** (`develop` branch): Automated deployments for QA
- **Staging** (`staging` branch): Pre-production validation
- **Production** (`main` branch): Stable releases with approval gates

## Quick Start

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd Datascience-ArtificialIntelligence-Webpage
```

### 2. Local Development

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up

# Access at http://localhost:8501
```

### 3. Run Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html
```

## Environment Setup

### Azure Login

```bash
# Login to Azure
az login

# Set default subscription
az account set --subscription "Your-Subscription-Name"

# Verify
az account show
```

### GitHub Secrets Configuration

Required secrets for GitHub Actions:

1. **AZURE_CREDENTIALS**: Service Principal credentials
2. **ACR_USERNAME**: Azure Container Registry username
3. **ACR_PASSWORD**: Azure Container Registry password

#### Create Service Principal

```bash
# Create service principal for GitHub Actions
az ad sp create-for-rbac --name "ml-visualizer-github-actions" \
  --role contributor \
  --scopes /subscriptions/{subscription-id} \
  --sdk-auth

# Save the output JSON to GitHub Secret: AZURE_CREDENTIALS
```

## Azure Infrastructure Deployment

### Deploy All Environments

```bash
# Make scripts executable
chmod +x infrastructure/deploy.sh infrastructure/destroy.sh

# Deploy testing environment
./infrastructure/deploy.sh testing westeurope

# Deploy staging environment
./infrastructure/deploy.sh staging westeurope

# Deploy production environment
./infrastructure/deploy.sh production westeurope
```

### What Gets Deployed

Each environment creates:

 **Resource Group**: Isolated resources per environment
 **Container Registry**: Docker image storage (shared or per-env)
 **App Service Plan**: Compute resources with auto-scaling
 **App Service**: Web application hosting
 **Application Insights**: Monitoring and analytics
 **Log Analytics**: Centralized logging
 **Alerts**: CPU, memory, error monitoring

### Manual Bicep Deployment

```bash
# Deploy using Azure CLI
az deployment sub create \
  --name ml-visualizer-production \
  --location westeurope \
  --template-file infrastructure/azure/main.bicep \
  --parameters environment=production location=westeurope
```

### Verify Deployment

```bash
# Check resource group
az group show --name ml-visualizer-production-rg

# List all resources
az resource list --resource-group ml-visualizer-production-rg --output table

# Get App Service URL
az webapp show --name ml-visualizer-production \
  --resource-group ml-visualizer-production-rg \
  --query defaultHostName -o tsv
```

## CI/CD Pipeline Configuration

### Branch Strategy

```
main (production)
  ↑
staging (pre-production)
  ↑
develop (testing)
  ↑
feature/* (development)
```

### Workflow Triggers

| Workflow | Trigger | Environment |
|----------|---------|-------------|
| `ci.yml` | Push/PR to all branches | N/A |
| `deploy-testing.yml` | Push to `develop` | Testing |
| `deploy-staging.yml` | Push to `staging` | Staging |
| `deploy-production.yml` | Push to `main` or tags | Production |

### Configuring GitHub Actions

1. **Add Repository Secrets**:
   ```
   Settings → Secrets and variables → Actions → New repository secret
   ```

2. **Required Secrets**:
   - `AZURE_CREDENTIALS`: Service principal JSON
   - `ACR_USERNAME`: Container registry username
   - `ACR_PASSWORD`: Container registry password

3. **Environment Protection Rules**:
   ```
   Settings → Environments → production-approval
   └─ Required reviewers: [Add team members]
   ```

### Update Workflow Variables

Edit `.github/workflows/*.yml`:

```yaml
env:
  AZURE_WEBAPP_NAME: ml-visualizer-production  # Update
  ACR_NAME: mlvisualizerregistry               # Update
  RESOURCE_GROUP: ml-visualizer-rg             # Update
```

## Application Deployment

### Automatic Deployment

Push to the appropriate branch:

```bash
# Deploy to testing
git checkout develop
git push origin develop

# Deploy to staging
git checkout staging
git merge develop
git push origin staging

# Deploy to production
git checkout main
git merge staging
git push origin main
```

### Manual Deployment

```bash
# Build and push image
docker build -t ml-visualizer:1.0.0 .

# Tag for ACR
docker tag ml-visualizer:1.0.0 \
  mlvisualizerregistry.azurecr.io/ml-visualizer:1.0.0

# Login to ACR
az acr login --name mlvisualizerregistry

# Push image
docker push mlvisualizerregistry.azurecr.io/ml-visualizer:1.0.0

# Deploy to App Service
az webapp config container set \
  --name ml-visualizer-production \
  --resource-group ml-visualizer-production-rg \
  --docker-custom-image-name mlvisualizerregistry.azurecr.io/ml-visualizer:1.0.0

# Restart app service
az webapp restart \
  --name ml-visualizer-production \
  --resource-group ml-visualizer-production-rg
```

### Rollback Procedure

```bash
# List previous images
az acr repository show-tags \
  --name mlvisualizerregistry \
  --repository ml-visualizer \
  --orderby time_desc

# Deploy previous version
az webapp config container set \
  --name ml-visualizer-production \
  --resource-group ml-visualizer-production-rg \
  --docker-custom-image-name mlvisualizerregistry.azurecr.io/ml-visualizer:1.0.0-previous
```

## Scaling and Performance

### Auto-Scaling Configuration

Auto-scaling is configured in Bicep templates:

- **Scale out**: When CPU > 70% or Memory > 80%
- **Scale in**: When CPU < 30% for 10 minutes
- **Min instances**: 1 (testing), 1 (staging), 2 (production)
- **Max instances**: 3 (testing), 5 (staging), 10 (production)

### Manual Scaling

```bash
# Scale out
az appservice plan update \
  --name ml-visualizer-production-plan \
  --resource-group ml-visualizer-production-rg \
  --number-of-workers 5

# Scale up (change tier)
az appservice plan update \
  --name ml-visualizer-production-plan \
  --resource-group ml-visualizer-production-rg \
  --sku P2v3
```

### Performance Tuning

**App Service Settings**:

```bash
# Enable Always On
az webapp config set \
  --name ml-visualizer-production \
  --resource-group ml-visualizer-production-rg \
  --always-on true

# Set health check path
az webapp config set \
  --name ml-visualizer-production \
  --resource-group ml-visualizer-production-rg \
  --health-check-path "/_stcore/health"
```

**Container Settings**:

- CPU Limit: 2 cores (production)
- Memory Limit: 4GB (production)
- Startup timeout: 230 seconds

## Monitoring and Alerts

### Application Insights

Access metrics:

```bash
# Portal
https://portal.azure.com → Application Insights → ml-visualizer-production-insights

# CLI
az monitor app-insights component show \
  --app ml-visualizer-production-insights \
  --resource-group ml-visualizer-production-rg
```

### Available Metrics

- Request rate and response time
- Failed requests (4xx, 5xx)
- CPU and memory usage
- Active connections
- Health check status

### Configured Alerts

| Alert | Threshold | Action |
|-------|-----------|--------|
| High CPU | > 80% for 15 min | Email notification |
| High Memory | > 85% for 15 min | Email notification |
| HTTP 5xx Errors | > 10 in 5 min | Email notification |
| Slow Response | > 5s average | Warning only |

### View Logs

```bash
# Stream logs
az webapp log tail \
  --name ml-visualizer-production \
  --resource-group ml-visualizer-production-rg

# Download logs
az webapp log download \
  --name ml-visualizer-production \
  --resource-group ml-visualizer-production-rg \
  --log-file logs.zip
```

## Troubleshooting

### Common Issues

#### 1. Container Failed to Start

```bash
# Check logs
az webapp log tail --name ml-visualizer-production \
  --resource-group ml-visualizer-production-rg

# Check container settings
az webapp config container show \
  --name ml-visualizer-production \
  --resource-group ml-visualizer-production-rg
```

#### 2. High Memory Usage

```bash
# Check current usage
az monitor metrics list \
  --resource /subscriptions/{sub-id}/resourceGroups/ml-visualizer-production-rg/providers/Microsoft.Web/sites/ml-visualizer-production \
  --metric MemoryPercentage

# Scale up if needed
az appservice plan update \
  --name ml-visualizer-production-plan \
  --resource-group ml-visualizer-production-rg \
  --sku P2v3
```

#### 3. Deployment Failed

```bash
# Check deployment status
az webapp deployment list-publishing-credentials \
  --name ml-visualizer-production \
  --resource-group ml-visualizer-production-rg

# Verify ACR credentials
az acr credential show --name mlvisualizerregistry

# Test image locally
docker pull mlvisualizerregistry.azurecr.io/ml-visualizer:latest
docker run -p 8501:8501 mlvisualizerregistry.azurecr.io/ml-visualizer:latest
```

#### 4. Health Check Failing

```bash
# Check health endpoint
curl https://ml-visualizer-production.azurewebsites.net/_stcore/health

# Check app service health
az webapp show \
  --name ml-visualizer-production \
  --resource-group ml-visualizer-production-rg \
  --query state
```

### Debug Mode

Enable detailed logging:

```bash
az webapp config appsettings set \
  --name ml-visualizer-production \
  --resource-group ml-visualizer-production-rg \
  --settings LOG_LEVEL=DEBUG ENABLE_DEBUG_MODE=true
```

### Support Resources

- [Azure App Service Documentation](https://docs.microsoft.com/azure/app-service/)
- [Azure Container Registry](https://docs.microsoft.com/azure/container-registry/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [GitHub Actions Documentation](https://docs.github.com/actions)

## Maintenance

### Regular Tasks

- **Weekly**: Review Application Insights metrics
- **Monthly**: Check for dependency updates
- **Quarterly**: Review and optimize costs
- **Annually**: Review security and compliance

### Backup Strategy

App Service automatically creates backups. To create manual backup:

```bash
az webapp config backup create \
  --resource-group ml-visualizer-production-rg \
  --webapp-name ml-visualizer-production \
  --backup-name manual-backup-$(date +%Y%m%d)
```

### Cost Optimization

```bash
# View costs
az consumption usage list \
  --start-date 2025-01-01 \
  --end-date 2025-01-31

# Stop non-production environments when not in use
az webapp stop --name ml-visualizer-testing \
  --resource-group ml-visualizer-testing-rg
```

---

**Version**: 1.0.0
**Last Updated**: December 2025
**Maintained By**: DevOps Team
