#!/bin/bash

# Production-Ready Azure Environment Setup Script
# Creates all necessary Azure resources for multi-environment deployment

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if required environment variables are set
check_prerequisites() {
    log_info "Checking prerequisites..."

    local required_vars=("AZURE_RESOURCE_GROUP" "AZURE_APP_SERVICE_PLAN" "AZURE_WEBAPP_NAME" "ACR_NAME" "AZURE_SUBSCRIPTION_ID")
    local missing_vars=()

    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            missing_vars+=("$var")
        fi
    done

    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Missing required environment variables:"
        printf '%s\n' "${missing_vars[@]}"
        echo
        echo "Please set the following variables:"
        echo "export AZURE_RESOURCE_GROUP=\"your-resource-group\""
        echo "export AZURE_APP_SERVICE_PLAN=\"your-app-service-plan\""
        echo "export AZURE_WEBAPP_NAME=\"your-webapp-name\""
        echo "export ACR_NAME=\"your-acr-name\""
        echo "export AZURE_SUBSCRIPTION_ID=\"your-subscription-id\""
        exit 1
    fi

    # Check if Azure CLI is installed
    if ! command -v az &> /dev/null; then
        log_error "Azure CLI is not installed. Please install it first."
        echo "Installation instructions: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    fi

    # Check if logged in to Azure
    if ! az account show &> /dev/null; then
        log_error "Not logged in to Azure. Please run 'az login' first."
        exit 1
    fi

    log_success "All prerequisites met"
}

# Set active subscription
set_subscription() {
    log_info "Setting active subscription to: $AZURE_SUBSCRIPTION_ID"
    az account set --subscription "$AZURE_SUBSCRIPTION_ID"
    log_success "Subscription set successfully"
}

# Check if resource group exists
check_resource_group() {
    log_info "Checking resource group: $AZURE_RESOURCE_GROUP"
    if az group show --name "$AZURE_RESOURCE_GROUP" &> /dev/null; then
        log_success "Resource group exists"
    else
        log_error "Resource group '$AZURE_RESOURCE_GROUP' does not exist"
        read -p "Create resource group? (y/N): " -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            create_resource_group
        else
            exit 1
        fi
    fi
}

# Create resource group
create_resource_group() {
    log_info "Creating resource group: $AZURE_RESOURCE_GROUP"
    read -p "Enter location (e.g., eastus, westeurope): " -r location
    az group create \
        --name "$AZURE_RESOURCE_GROUP" \
        --location "$location"
    log_success "Resource group created"
}

# Check if app service plan exists
check_app_service_plan() {
    log_info "Checking app service plan: $AZURE_APP_SERVICE_PLAN"
    if az appservice plan show \
        --name "$AZURE_APP_SERVICE_PLAN" \
        --resource-group "$AZURE_RESOURCE_GROUP" &> /dev/null; then
        log_success "App service plan exists"
    else
        log_error "App service plan '$AZURE_APP_SERVICE_PLAN' does not exist"
        read -p "Create app service plan? (y/N): " -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            create_app_service_plan
        else
            exit 1
        fi
    fi
}

# Create app service plan
create_app_service_plan() {
    log_info "Creating app service plan: $AZURE_APP_SERVICE_PLAN"
    echo "Available SKUs:"
    echo "  B1 (Basic) - For development/testing"
    echo "  S1 (Standard) - For staging environments"
    echo "  P1V2 (Premium) - For production workloads"
    echo "  P2V2 (Premium) - For high-performance production"

    read -p "Enter SKU (B1/S1/P1V2/P2V2): " -r sku

    az appservice plan create \
        --name "$AZURE_APP_SERVICE_PLAN" \
        --resource-group "$AZURE_RESOURCE_GROUP" \
        --sku "${sku:-B1}" \
        --is-linux
    log_success "App service plan created"
}

# Check if container registry exists
check_container_registry() {
    log_info "Checking container registry: $ACR_NAME"
    if az acr show --name "$ACR_NAME" &> /dev/null; then
        log_success "Container registry exists"
    else
        log_error "Container registry '$ACR_NAME' does not exist"
        read -p "Create container registry? (y/N): " -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            create_container_registry
        else
            exit 1
        fi
    fi
}

# Create container registry
create_container_registry() {
    log_info "Creating container registry: $ACR_NAME"
    echo "Available SKUs:"
    echo "  Basic - For development (5 GB storage, 10 GiB transfer/month)"
    echo "  Standard - For production (100 GB storage, 100 GiB transfer/month)"
    echo "  Premium - For enterprise (500 GB storage, 500 GiB transfer/month)"

    read -p "Enter SKU (Basic/Standard/Premium): " -r sku

    az acr create \
        --resource-group "$AZURE_RESOURCE_GROUP" \
        --name "$ACR_NAME" \
        --sku "${sku:-Basic}" \
        --admin-enabled true
    log_success "Container registry created"
}

# Create web app
create_web_app() {
    local app_name="$1"
    local environment="$2"

    log_info "Creating web app: $app_name ($environment environment)"

    if az webapp show --name "$app_name" --resource-group "$AZURE_RESOURCE_GROUP" &> /dev/null; then
        log_warning "Web app '$app_name' already exists"
        return
    fi

    az webapp create \
        --resource-group "$AZURE_RESOURCE_GROUP" \
        --plan "$AZURE_APP_SERVICE_PLAN" \
        --name "$app_name" \
        --deployment-container-image-name "${ACR_NAME}.azurecr.io/ml-visualizer:latest"

    # Configure container settings
    log_info "Configuring container settings for $app_name"
    az webapp config container set \
        --name "$app_name" \
        --resource-group "$AZURE_RESOURCE_GROUP" \
        --container-image-name "${ACR_NAME}.azurecr.io/ml-visualizer:latest" \
        --container-registry-url "https://${ACR_NAME}.azurecr.io"

    # Configure app settings
    az webapp config appsettings set \
        --resource-group "$AZURE_RESOURCE_GROUP" \
        --name "$app_name" \
        --settings \
            "ENVIRONMENT=$environment" \
            "WEBSITES_PORT=8501" \
            "WEBSITES_ENABLE_APP_SERVICE_STORAGE=false"

    log_success "Web app '$app_name' created and configured"
}

# Setup environments
setup_environments() {
    log_info "Setting up production"

    # Check if production environment exists, create if not
    if ! az webapp show --name "$AZURE_WEBAPP_NAME" --resource-group "$AZURE_RESOURCE_GROUP" &> /dev/null; then
        create_web_app "$AZURE_WEBAPP_NAME" "production"
    else
        log_success "Production web app '$AZURE_WEBAPP_NAME' already exists"
    fi
}

# Create service principal for CI/CD
create_service_principal() {
    log_info "Creating service principal for CI/CD"

    local sp_name="ml-visualizer-cicd-sp"
    local subscription_id="$AZURE_SUBSCRIPTION_ID"

    # Check if service principal already exists
    local existing_sp=$(az ad sp list --display-name "$sp_name" --query "[0].appId" -o tsv 2>/dev/null || echo "")

    if [[ -n "$existing_sp" && "$existing_sp" != "null" ]]; then
        log_warning "Service principal '$sp_name' already exists with App ID: $existing_sp"
        read -p "Use existing service principal? (y/N): " -r
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
    else
        log_info "Creating new service principal: $sp_name"
        local sp_output
        sp_output=$(az ad sp create-for-rbac \
            --name "$sp_name" \
            --role "Contributor" \
            --scopes "/subscriptions/$subscription_id/resourceGroups/$AZURE_RESOURCE_GROUP" \
            --json-auth)

        local app_id=$(echo "$sp_output" | jq -r '.clientId')
        local client_secret=$(echo "$sp_output" | jq -r '.clientSecret')
        local tenant_id=$(echo "$sp_output" | jq -r '.tenantId')

        echo
        log_success "Service principal created successfully!"
        echo "========================================"
        echo "GITLAB CI/CD VARIABLES:"
        echo "========================================"
        echo "AZURE_SUBSCRIPTION_ID = $subscription_id"
        echo "AZURE_RESOURCE_GROUP = $AZURE_RESOURCE_GROUP"
        echo "AZURE_APP_SERVICE_PLAN = $AZURE_APP_SERVICE_PLAN"
        echo "AZURE_WEBAPP_NAME = $AZURE_WEBAPP_NAME"
        echo "ACR_NAME = $ACR_NAME"
        echo "AZURE_CLIENT_ID = $app_id"
        echo "AZURE_CLIENT_SECRET = $client_secret (PROTECT THIS)"
        echo "AZURE_TENANT_ID = $tenant_id"
        echo "========================================"
        echo
        log_warning "IMPORTANT: Copy these values to your GitLab CI/CD variables!"
        log_warning "Mark AZURE_CLIENT_SECRET as protected and masked!"
    fi

    # Grant ACR permissions
    log_info "Granting ACR permissions to service principal"
    local app_id_to_use="${app_id:-$existing_sp}"
    az role assignment create \
        --assignee "$app_id_to_use" \
        --role "AcrPull" \
        --scope "/subscriptions/$subscription_id/resourceGroups/$AZURE_RESOURCE_GROUP/providers/Microsoft.ContainerRegistry/registries/$ACR_NAME"

    az role assignment create \
        --assignee "$app_id_to_use" \
        --role "AcrPush" \
        --scope "/subscriptions/$subscription_id/resourceGroups/$AZURE_RESOURCE_GROUP/providers/Microsoft.ContainerRegistry/registries/$ACR_NAME"

    log_success "ACR permissions granted"
}

# Display environment URLs
display_environment_info() {
    echo
    log_success "=== ENVIRONMENT SETUP COMPLETE ==="
    echo
    echo "Environment URLs:"
    echo "  Production: https://${AZURE_WEBAPP_NAME}.azurewebsites.net"
    echo
    echo "Container Registry:"
    echo "  URL: ${ACR_NAME}.azurecr.io"
    echo "  Repository: ${ACR_NAME}.azurecr.io/ml-visualizer"
    echo
    echo "Next steps:"
    echo "1. Configure GitLab CI/CD variables (see output above)"
    echo "2. Push code to trigger first deployment"
    echo "3. Test deployments on each environment"
    echo
    log_info "Setup completed successfully!"
}

# Main execution
main() {
    echo "======================================================"
    echo "ML Visualizer Production Environment Setup"
    echo "======================================================"
    echo

    check_prerequisites
    set_subscription
    check_resource_group
    check_app_service_plan
    check_container_registry
    setup_environments
    create_service_principal
    display_environment_info
}

# Execute main function
main "$@"
