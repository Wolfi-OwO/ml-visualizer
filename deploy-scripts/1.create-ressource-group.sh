#!/bin/bash
set -e

RESOURCE_GROUP=$1
LOCATION=$2

if [[ -z "$RESOURCE_GROUP" || -z "$LOCATION" ]]; then
  echo "Usage: $0 <resource_group> <location>"
  exit 1
fi

echo "Creating resource group $RESOURCE_GROUP..."
az group create --name $RESOURCE_GROUP \
    --location $LOCATION \
    --output table

echo ""
echo "=========================================="
echo "Resource Group Created!"
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "=========================================="
echo ""
