# ML Visualizer - Complete Setup Guide

This guide walks you through setting up the ML Visualizer application from scratch, including local development, Azure infrastructure, and CI/CD pipelines.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Azure Infrastructure Setup](#azure-infrastructure-setup)
4. [CI/CD Pipeline Configuration](#cicd-pipeline-configuration)
5. [Deployment Workflow](#deployment-workflow)
6. [Verification and Testing](#verification-and-testing)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

Install the following tools before proceeding:

**Azure CLI** (version 2.50 or higher)
```bash
# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# macOS
brew install azure-cli

# Windows
# Download from: https://aka.ms/installazurecliwindows

# Verify installation
az --version
```

**Docker and Docker Compose**
```bash
# Linux (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install docker.io docker-compose-plugin

# macOS
brew install docker docker-compose

# Windows
# Download Docker Desktop from: https://www.docker.com/products/docker-desktop

# Verify installation
docker --version
docker compose version
```

**Python 3.12 or higher**
```bash
# Linux
sudo apt-get install python3.12 python3.12-venv

# macOS
brew install python@3.12

# Windows
# Download from: https://www.python.org/downloads/

# Verify installation
python3 --version
```

**Git**
```bash
# Most systems have git pre-installed
git --version

# If not installed:
# Linux: sudo apt-get install git
# macOS: brew install git
# Windows: https://git-scm.com/download/win
```

### Azure Requirements

- Active Azure subscription
- Contributor role on the subscription
- Ability to create resource groups and resources

### GitHub/GitLab Requirements

- Repository access (read/write permissions)
- Ability to configure CI/CD secrets
- Ability to create protected branches

## Local Development Setup

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone <your-repository-url>
cd Datascience-ArtificialIntelligence-Webpage

# Verify repository structure
ls -la
```

Expected directories:
- `.github/workflows` - CI/CD pipelines
- `config/` - Environment configurations
- `infrastructure/` - Azure Bicep templates
- `src/` - Application source code
- `tests/` - Test suite
- `docker/` - Docker configurations

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Verify activation (should show venv path)
which python3
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pre-commit ruff pytest pytest-cov
```

### Step 4: Configure Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Test pre-commit hooks (optional)
pre-commit run --all-files
```

### Step 5: Start Local Development Server

**Option A: Using Docker Compose (Recommended)**
```bash
# Start development environment with hot reload
docker compose -f docker-compose.dev.yml up

# The application will be available at:
# http://localhost:8501
```

**Option B: Without Docker**
```bash
# Set environment variables
export ENVIRONMENT_NAME=development
export LOG_LEVEL=DEBUG

# Start Streamlit application
streamlit run src/app.py

# The application will be available at:
# http://localhost:8501
```

### Step 6: Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Step 7: Verify Local Setup

Visit http://localhost:8501 and verify:
- Application loads without errors
- All navigation pages are accessible:
  - Gradient Descent
  - Perceptron
  - KNN Visualizer
  - Neuronal Network
- Visualizations render correctly

## Azure Infrastructure Setup

### Step 1: Azure Login

```bash
# Login to Azure
az login

# List available subscriptions
az account list --output table

# Set active subscription
az account set --subscription "Your-Subscription-Name"

# Verify current account
az account show --output table
```

### Step 2: Verify Permissions

```bash
# Check your role assignments
az role assignment list --assignee $(az account show --query user.name -o tsv) --output table

# You need at least "Contributor" role
```

### Step 3: Choose Azure Region

Select a region close to your users:
- `westeurope` - West Europe (Netherlands)
- `eastus` - East US (Virginia)
- `westus2` - West US 2 (Washington)
- `southeastasia` - Southeast Asia (Singapore)

```bash
# List available regions
az account list-locations --output table

# Set your preferred region
export AZURE_REGION=westeurope
```

### Step 4: Deploy Testing Environment

```bash
# Make deployment script executable
chmod +x infrastructure/deploy.sh

# Deploy testing environment
./infrastructure/deploy.sh testing $AZURE_REGION

# Wait for deployment (typically 5-10 minutes)
# Save the output - it contains important information
```

Expected output includes:
- Resource Group name
- Container Registry name and login server
- App Service name and URL
- Application Insights instrumentation key

Save these values for later use.

### Step 5: Deploy Staging Environment

```bash
# Deploy staging environment
./infrastructure/deploy.sh staging $AZURE_REGION

# Save the output
```

### Step 6: Deploy Production Environment

```bash
# Deploy production environment
./infrastructure/deploy.sh production $AZURE_REGION

# Save the output securely
```

### Step 7: Verify Azure Resources

```bash
# List all resource groups
az group list --output table | grep ml-visualizer

# Check testing resources
az resource list --resource-group ml-visualizer-testing-rg --output table

# Check staging resources
az resource list --resource-group ml-visualizer-staging-rg --output table

# Check production resources
az resource list --resource-group ml-visualizer-production-rg --output table
```

### Step 8: Retrieve Container Registry Credentials

```bash
# Get ACR name (from deployment output)
ACR_NAME=$(az acr list --resource-group ml-visualizer-testing-rg --query "[0].name" -o tsv)

# Get ACR credentials
az acr credential show --name $ACR_NAME

# Save these credentials - you'll need them for CI/CD
```

Output will show:
- `username` - Use for ACR_USERNAME secret
- `passwords[0].value` - Use for ACR_PASSWORD secret

## CI/CD Pipeline Configuration

### Step 1: Create Azure Service Principal

```bash
# Get your subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Create service principal for GitHub Actions
az ad sp create-for-rbac \
  --name "ml-visualizer-cicd" \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID \
  --sdk-auth

# IMPORTANT: Save the entire JSON output securely
# This will be used for AZURE_CREDENTIALS secret
```

The output JSON should look like:
```json
{
  "clientId": "...",
  "clientSecret": "...",
  "subscriptionId": "...",
  "tenantId": "...",
  ...
}
```

### Step 2: Configure GitHub Secrets

Navigate to your GitHub repository:
1. Go to: Settings > Secrets and variables > Actions
2. Click "New repository secret"

Add the following secrets:

**AZURE_CREDENTIALS**
- Value: The entire JSON output from service principal creation
- Used for: Azure authentication in workflows

**ACR_USERNAME**
- Value: Username from `az acr credential show`
- Used for: Container registry authentication

**ACR_PASSWORD**
- Value: Password from `az acr credential show`
- Used for: Container registry authentication

Verify secrets are added:
```bash
# If you have GitHub CLI installed
gh secret list
```

### Step 3: Configure GitHub Environments

Create protected environments:

1. Go to: Settings > Environments
2. Create the following environments:

**testing**
- No protection rules needed
- Auto-deploys from `develop` branch

**staging**
- Optional: Add deployment protection rules
- Auto-deploys from `staging` branch

**production**
- Click "Add protection rule"
- Check "Required reviewers"
- Add yourself and/or team members
- Deploys from `main` branch after approval

**production-approval**
- Click "Add protection rule"
- Check "Required reviewers"
- Add reviewers who can approve production deployments

### Step 4: Update Workflow Configuration

Edit workflow files to match your Azure resources:

**File: .github/workflows/deploy-testing.yml**
```yaml
env:
  AZURE_WEBAPP_NAME: ml-visualizer-testing  # Update if different
  ACR_NAME: <your-acr-name>                 # From Step 8
  IMAGE_NAME: ml-visualizer
  RESOURCE_GROUP: ml-visualizer-testing-rg
```

**File: .github/workflows/deploy-staging.yml**
```yaml
env:
  AZURE_WEBAPP_NAME: ml-visualizer-staging
  ACR_NAME: <your-acr-name>
  IMAGE_NAME: ml-visualizer
  RESOURCE_GROUP: ml-visualizer-staging-rg
```

**File: .github/workflows/deploy-production.yml**
```yaml
env:
  AZURE_WEBAPP_NAME: ml-visualizer-prod
  ACR_NAME: <your-acr-name>
  IMAGE_NAME: ml-visualizer
  RESOURCE_GROUP: ml-visualizer-production-rg
```

Replace `<your-acr-name>` with your actual Container Registry name.

### Step 5: Configure Branch Protection

1. Go to: Settings > Branches
2. Add branch protection rules:

**For `main` branch:**
- Require pull request reviews before merging
- Require status checks to pass before merging
  - Select: CI / test
- Require branches to be up to date before merging

**For `staging` branch:**
- Require pull request reviews before merging
- Require status checks to pass before merging

**For `develop` branch:**
- Require status checks to pass before merging

## Deployment Workflow

### Branch Strategy

```
feature/xyz → develop → staging → main
             (testing) (staging) (production)
```

### Initial Deployment

**Step 1: Prepare Code**
```bash
# Ensure you're on develop branch
git checkout develop

# Make sure code is up to date
git pull origin develop

# Verify tests pass locally
pytest tests/ -v
```

**Step 2: Deploy to Testing**
```bash
# Push to develop branch
git push origin develop

# This triggers automatic deployment to testing environment
# Monitor progress at: https://github.com/your-repo/actions
```

**Step 3: Verify Testing Deployment**
```bash
# Check deployment status
az webapp show \
  --name ml-visualizer-testing \
  --resource-group ml-visualizer-testing-rg \
  --query state -o tsv

# Test health endpoint
curl https://ml-visualizer-testing.azurewebsites.net/_stcore/health

# Visit the application
open https://ml-visualizer-testing.azurewebsites.net
```

**Step 4: Deploy to Staging**
```bash
# Merge develop to staging
git checkout staging
git merge develop
git push origin staging

# Monitor deployment at GitHub Actions
```

**Step 5: Verify Staging Deployment**
```bash
# Check deployment status
az webapp show \
  --name ml-visualizer-staging \
  --resource-group ml-visualizer-staging-rg \
  --query state -o tsv

# Test application
curl https://ml-visualizer-staging.azurewebsites.net/_stcore/health
open https://ml-visualizer-staging.azurewebsites.net
```

**Step 6: Deploy to Production**
```bash
# Merge staging to main
git checkout main
git merge staging
git push origin main

# GitHub Actions will start but wait for approval
# Go to: https://github.com/your-repo/actions
# Find the workflow run
# Click "Review deployments"
# Select "production-approval"
# Click "Approve and deploy"
```

**Step 7: Verify Production Deployment**
```bash
# Wait for deployment to complete (check GitHub Actions)

# Check deployment status
az webapp show \
  --name ml-visualizer-prod \
  --resource-group ml-visualizer-production-rg \
  --query state -o tsv

# Test health endpoint
curl https://ml-visualizer-prod.azurewebsites.net/_stcore/health

# Visit production application
open https://ml-visualizer-prod.azurewebsites.net

# Verify all pages work correctly
```

## Verification and Testing

### Health Checks

```bash
# Testing environment
curl -f https://ml-visualizer-testing.azurewebsites.net/_stcore/health && echo "OK" || echo "FAILED"

# Staging environment
curl -f https://ml-visualizer-staging.azurewebsites.net/_stcore/health && echo "OK" || echo "FAILED"

# Production environment
curl -f https://ml-visualizer-prod.azurewebsites.net/_stcore/health && echo "OK" || echo "FAILED"
```

All should return "OK"

### Monitor Application Insights

```bash
# Open Application Insights for production
az monitor app-insights component show \
  --app ml-visualizer-production-insights \
  --resource-group ml-visualizer-production-rg \
  --query appId -o tsv

# Open in browser
open "https://portal.azure.com/#@/resource/subscriptions/$SUBSCRIPTION_ID/resourceGroups/ml-visualizer-production-rg/providers/microsoft.insights/components/ml-visualizer-production-insights"
```

Verify:
- Requests are being logged
- No errors in logs
- Performance metrics are normal

### Check Logs

```bash
# Stream logs from production
az webapp log tail \
  --name ml-visualizer-prod \
  --resource-group ml-visualizer-production-rg

# Press Ctrl+C to stop streaming
```

### Verify Auto-Scaling

```bash
# Check auto-scale settings
az monitor autoscale show \
  --resource-group ml-visualizer-production-rg \
  --name ml-visualizer-production-autoscale \
  --output table

# Check current instance count
az appservice plan show \
  --name ml-visualizer-production-plan \
  --resource-group ml-visualizer-production-rg \
  --query sku.capacity -o tsv
```

## Troubleshooting

### Common Issues and Solutions

**Issue: Docker build fails locally**
```bash
# Clear Docker cache
docker system prune -a -f

# Rebuild without cache
docker compose -f docker-compose.dev.yml build --no-cache

# Check Docker disk space
docker system df
```

**Issue: Azure CLI not authenticated**
```bash
# Re-login
az logout
az login

# Clear cached credentials
rm -rf ~/.azure

# Login again
az login
```

**Issue: Deployment script fails**
```bash
# Check Azure CLI version
az --version  # Should be 2.50+

# Update Azure CLI
# Linux: sudo apt-get update && sudo apt-get upgrade azure-cli
# macOS: brew upgrade azure-cli

# Verify permissions
az role assignment list --assignee $(az account show --query user.name -o tsv)
```

**Issue: Container fails to start in Azure**
```bash
# Check container logs
az webapp log tail --name ml-visualizer-testing --resource-group ml-visualizer-testing-rg

# Check container settings
az webapp config container show \
  --name ml-visualizer-testing \
  --resource-group ml-visualizer-testing-rg

# Verify image exists in ACR
az acr repository list --name <acr-name> --output table
az acr repository show-tags --name <acr-name> --repository ml-visualizer --output table
```

**Issue: GitHub Actions workflow fails**
```bash
# Check secrets are configured
gh secret list

# Verify service principal has permissions
az role assignment list --assignee <service-principal-client-id>

# Test ACR login manually
az acr login --name <acr-name>
```

**Issue: Application not accessible**
```bash
# Check app service status
az webapp show \
  --name ml-visualizer-prod \
  --resource-group ml-visualizer-production-rg \
  --query state

# Restart app service
az webapp restart \
  --name ml-visualizer-prod \
  --resource-group ml-visualizer-production-rg

# Check for any stopped services
az webapp list --resource-group ml-visualizer-production-rg --query "[?state!='Running']" --output table
```

**Issue: High memory or CPU usage**
```bash
# Check current metrics
az monitor metrics list \
  --resource /subscriptions/$SUBSCRIPTION_ID/resourceGroups/ml-visualizer-production-rg/providers/Microsoft.Web/sites/ml-visualizer-prod \
  --metric CpuPercentage,MemoryPercentage \
  --output table

# Scale up if needed
az appservice plan update \
  --name ml-visualizer-production-plan \
  --resource-group ml-visualizer-production-rg \
  --sku P2v3
```

### Getting Help

**View detailed logs:**
```bash
# Download all logs
az webapp log download \
  --name ml-visualizer-prod \
  --resource-group ml-visualizer-production-rg \
  --log-file logs.zip

# Extract and review
unzip logs.zip
```

**Check deployment history:**
```bash
# List recent deployments
az deployment group list \
  --resource-group ml-visualizer-production-rg \
  --output table

# Show specific deployment
az deployment group show \
  --resource-group ml-visualizer-production-rg \
  --name <deployment-name>
```

## Next Steps

After successful setup:

1. **Configure Custom Domain** (Optional)
   ```bash
   az webapp config hostname add \
     --webapp-name ml-visualizer-prod \
     --resource-group ml-visualizer-production-rg \
     --hostname www.yourdomain.com
   ```

2. **Set up SSL Certificate** (Optional)
   - Use Azure Managed Certificate (free)
   - Or bring your own certificate

3. **Configure Monitoring Alerts**
   - Review alert rules in Application Insights
   - Add email notifications
   - Set up SMS alerts for critical issues

4. **Review Costs**
   ```bash
   # Check current costs
   az consumption usage list --output table
   
   # Set up cost alerts in Azure Portal
   ```

5. **Schedule Regular Maintenance**
   - Update dependencies monthly
   - Review security advisories
   - Test disaster recovery procedures quarterly

## Summary

You have now:
- Set up local development environment
- Deployed Azure infrastructure for all environments
- Configured CI/CD pipelines
- Deployed the application to testing, staging, and production
- Verified all components are working

The application is now production-ready with:
- Automated testing on every commit
- Auto-scaling based on load
- Comprehensive monitoring and alerting
- Three-tier environment progression
- Approval gates for production deployments

For ongoing operations, refer to:
- `DEPLOYMENT_CHECKLIST.md` for deployment procedures
- `QUICK_REFERENCE.md` for common commands
- `config/README.md` for configuration options

---

**Setup Version**: 1.0.0  
**Last Updated**: December 2025  
**Author**: DevOps Team
