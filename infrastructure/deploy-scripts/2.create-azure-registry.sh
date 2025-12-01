#!/bin/bash
set -e

RESOURCE_GROUP=$1
ACR_NAME=$2

if [[ -z "$RESOURCE_GROUP" || -z "$ACR_NAME" ]]; then
  echo "Usage: $0 <resource_group> <acr_name>"
  exit 1
fi

echo "Creating Azure Container Registry $ACR_NAME..."
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled false \
    --output table

echo ""
echo "=========================================="
echo "ACR Setup Complete!"
echo "=========================================="
echo ""
echo "Registry: $ACR_NAME.azurecr.io"
echo "Authentication: Managed Identity / Azure CLI"
echo ""
