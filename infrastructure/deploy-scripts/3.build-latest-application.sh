#!/bin/bash
set -e

IMAGE_NAME=$1
ACR_NAME=$2
VERSION=$3

if [[ -z "$IMAGE_NAME" || -z "$ACR_NAME" || -z "$VERSION" ]]; then
  echo "Usage: $0 <image_name> <acr_name> <version>"
  exit 1
fi

FULL_VERSION_TAG="$ACR_NAME.azurecr.io/$IMAGE_NAME:$VERSION"
LATEST_TAG="$ACR_NAME.azurecr.io/$IMAGE_NAME:latest"

echo "Logging into ACR..."
az acr login --name $ACR_NAME

echo "Building Docker image..."
# Navigate to project root (two directories up from deploy-scripts)
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
docker build -t $IMAGE_NAME "$PROJECT_ROOT"

# Tag the Docker image with both the version and latest
docker tag $IMAGE_NAME $FULL_VERSION_TAG
docker tag $IMAGE_NAME $LATEST_TAG

echo "Pushing Docker image tags to ACR..."
docker push $FULL_VERSION_TAG
docker push $LATEST_TAG

echo ""
echo "=========================================="
echo "Images pushed successfully!"
echo "  - $FULL_VERSION_TAG"
echo "  - $LATEST_TAG"
echo "=========================================="
echo ""
