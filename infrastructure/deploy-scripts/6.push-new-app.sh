#!/bin/bash
set -e

IMAGE_NAME=$1
ACR_NAME=$2
VERSION=$3
WEBAPP_NAME=$4
RESOURCE_GROUP=$5

if [[ -z "$IMAGE_NAME" || -z "$ACR_NAME" || -z "$VERSION" || -z "$WEBAPP_NAME" || -z "$RESOURCE_GROUP" ]]; then
  echo "Usage: $0 <image_name> <acr_name> <version> <webapp_name> <resource_group>"
  exit 1
fi

# Set the new image as the one to be used by the Web App
echo "Updating Web App $WEBAPP_NAME to use image $ACR_NAME.azurecr.io/$IMAGE_NAME:$VERSION ..."
az webapp config container set \
    --name $WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP \
    --container-image-name "$ACR_NAME.azurecr.io/$IMAGE_NAME:$VERSION" \
    --output table
