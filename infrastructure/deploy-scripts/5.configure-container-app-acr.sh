#!/bin/bash
set -e

CONTAINER_APP_NAME=$1
RESOURCE_GROUP=$2
ACR_NAME=$3
ACR_USERNAME=$4
ACR_PASSWORD=$5
IMAGE_NAME=$6
IMAGE_VERSION=$7

if [[ -z "$CONTAINER_APP_NAME" || -z "$RESOURCE_GROUP" || -z "$ACR_NAME" || -z "$ACR_USERNAME" || -z "$ACR_PASSWORD" || -z "$IMAGE_NAME" || -z "$IMAGE_VERSION" ]]; then
  echo "Usage: $0 <container_app_name> <resource_group> <acr_name> <acr_username> <acr_password> <image_name> <image_version>"
  exit 1
fi

echo "Configuring Container App to pull from Azure Container Registry..."
echo "Container App: $CONTAINER_APP_NAME"
echo "Registry: $ACR_NAME.azurecr.io"
echo "Image: $IMAGE_NAME:$IMAGE_VERSION"
echo ""

# Update container app with ACR image and credentials
echo "Updating Container App image..."
az containerapp update \
    --name "$CONTAINER_APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --image "$ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_VERSION" \
    --registry-server "$ACR_NAME.azurecr.io" \
    --registry-username "$ACR_USERNAME" \
    --registry-password "$ACR_PASSWORD" \
    --output table

echo ""
echo "✓ Container App updated successfully!"
echo ""
echo "Configuration Summary:"
echo "  - Container App: $CONTAINER_APP_NAME"
echo "  - Resource Group: $RESOURCE_GROUP"
echo "  - Registry: $ACR_NAME.azurecr.io"
echo "  - Image: $IMAGE_NAME:$IMAGE_VERSION"
echo ""
echo "The container app will now pull images from Azure Container Registry."
echo ""
