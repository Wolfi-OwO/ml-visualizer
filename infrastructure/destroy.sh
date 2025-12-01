#!/bin/bash
# Destroy Azure infrastructure for an environment
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

if [ -z "$1" ]; then
    print_error "Usage: $0 <environment>"
    print_info "Environments: testing, staging, production"
    exit 1
fi

ENVIRONMENT=$1
PROJECT_NAME="ml-visualizer"
RESOURCE_GROUP="${PROJECT_NAME}-${ENVIRONMENT}-rg"

if [[ ! "$ENVIRONMENT" =~ ^(testing|staging|production)$ ]]; then
    print_error "Invalid environment. Must be: testing, staging, or production"
    exit 1
fi

print_warning "⚠️  You are about to DELETE all resources in environment: $ENVIRONMENT"
print_warning "Resource Group: $RESOURCE_GROUP"
echo ""
read -p "Are you sure you want to continue? (type 'yes' to confirm): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    print_info "Aborted."
    exit 0
fi

print_info "Deleting resource group: $RESOURCE_GROUP"
az group delete --name "$RESOURCE_GROUP" --yes --no-wait

print_info "✅ Deletion initiated. Resources will be removed in the background."
print_info "Check status with: az group show --name $RESOURCE_GROUP"
