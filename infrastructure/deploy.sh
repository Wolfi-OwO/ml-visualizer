#!/bin/bash
# Deploy Azure infrastructure using Bicep templates
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if environment parameter is provided
if [ -z "$1" ]; then
    print_error "Usage: $0 <environment> [location]"
    print_info "Environments: testing, staging, production"
    exit 1
fi

ENVIRONMENT=$1
LOCATION=${2:-westeurope}
PROJECT_NAME="ml-visualizer"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(testing|staging|production)$ ]]; then
    print_error "Invalid environment. Must be: testing, staging, or production"
    exit 1
fi

print_info "Deploying infrastructure for environment: $ENVIRONMENT"
print_info "Location: $LOCATION"

# Check if logged in to Azure
print_info "Checking Azure login status..."
if ! az account show &> /dev/null; then
    print_error "Not logged in to Azure. Please run: az login"
    exit 1
fi

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
print_info "Using subscription: $SUBSCRIPTION_ID"

# Deploy the infrastructure
print_info "Starting Bicep deployment..."
DEPLOYMENT_NAME="${PROJECT_NAME}-${ENVIRONMENT}-$(date +%Y%m%d-%H%M%S)"

az deployment sub create \
    --name "$DEPLOYMENT_NAME" \
    --location "$LOCATION" \
    --template-file infrastructure/azure/main.bicep \
    --parameters environment="$ENVIRONMENT" location="$LOCATION" projectName="$PROJECT_NAME" \
    --output table

if [ $? -eq 0 ]; then
    print_info "✅ Deployment successful!"

    # Get outputs
    print_info "Fetching deployment outputs..."

    RESOURCE_GROUP=$(az deployment sub show --name "$DEPLOYMENT_NAME" --query properties.outputs.resourceGroupName.value -o tsv)
    ACR_NAME=$(az deployment sub show --name "$DEPLOYMENT_NAME" --query properties.outputs.acrName.value -o tsv)
    ACR_LOGIN_SERVER=$(az deployment sub show --name "$DEPLOYMENT_NAME" --query properties.outputs.acrLoginServer.value -o tsv)
    APP_SERVICE_NAME=$(az deployment sub show --name "$DEPLOYMENT_NAME" --query properties.outputs.appServiceName.value -o tsv)
    APP_SERVICE_URL=$(az deployment sub show --name "$DEPLOYMENT_NAME" --query properties.outputs.appServiceUrl.value -o tsv)

    echo ""
    print_info "=== Deployment Details ==="
    echo "Resource Group: $RESOURCE_GROUP"
    echo "Container Registry: $ACR_NAME"
    echo "ACR Login Server: $ACR_LOGIN_SERVER"
    echo "App Service Name: $APP_SERVICE_NAME"
    echo "App Service URL: $APP_SERVICE_URL"
    echo ""

    # Save outputs to file
    OUTPUT_FILE="infrastructure/outputs/${ENVIRONMENT}-outputs.json"
    mkdir -p infrastructure/outputs

    az deployment sub show --name "$DEPLOYMENT_NAME" --query properties.outputs -o json > "$OUTPUT_FILE"
    print_info "Outputs saved to: $OUTPUT_FILE"

    # Configure ACR credentials for App Service
    print_info "Configuring ACR credentials for App Service..."
    ACR_USERNAME=$(az acr credential show --name "$ACR_NAME" --query username -o tsv)
    ACR_PASSWORD=$(az acr credential show --name "$ACR_NAME" --query passwords[0].value -o tsv)

    az webapp config container set \
        --name "$APP_SERVICE_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --docker-registry-server-url "https://$ACR_LOGIN_SERVER" \
        --docker-registry-server-user "$ACR_USERNAME" \
        --docker-registry-server-password "$ACR_PASSWORD" \
        --output none

    print_info "✅ Infrastructure deployment complete!"
    print_info "Next steps:"
    echo "  1. Configure GitHub secrets with ACR credentials"
    echo "  2. Push your first image: docker push $ACR_LOGIN_SERVER/$PROJECT_NAME:latest"
    echo "  3. Access your app at: $APP_SERVICE_URL"

else
    print_error "❌ Deployment failed!"
    exit 1
fi
