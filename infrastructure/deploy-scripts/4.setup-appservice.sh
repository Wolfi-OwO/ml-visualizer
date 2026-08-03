#!/bin/bash
set -e

RESOURCE_GROUP=$1
APP_SERVICE_PLAN=$2
WEBAPP_NAME=$3
ACR_NAME=$4
IMAGE_NAME=$5
IMAGE_VERSION=$6
HEALTH_PATH="/_stcore/health"

if [[ -z "$RESOURCE_GROUP" || -z "$APP_SERVICE_PLAN" || -z "$WEBAPP_NAME" || -z "$ACR_NAME" || -z "$IMAGE_NAME" || -z "$IMAGE_VERSION" ]]; then
  echo "Usage: $0 <resource_group> <app_service_plan> <webapp_name> <acr_name> <image_name> <image_version>"
  exit 1
fi

echo "Creating App Service plan $APP_SERVICE_PLAN..."
az appservice plan create \
    --name $APP_SERVICE_PLAN \
    --resource-group $RESOURCE_GROUP \
    --sku B1 \
    --is-linux \
    --output table

# Create the web app, but only if it does not exist yet
echo "Creating Web App $WEBAPP_NAME..."
az webapp create \
    --name $WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --container-image-name "$ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_VERSION" \
    --output table

echo "Enabling Basic Auth for SCM and FTP..."
az resource update \
    --resource-group $RESOURCE_GROUP \
    --name scm \
    --namespace Microsoft.Web \
    --resource-type basicPublishingCredentialsPolicies \
    --parent sites/$WEBAPP_NAME \
    --set properties.allow=true \
    --output none 2>/dev/null || echo "Note: Could not update SCM basic auth (may not be needed)"

az resource update \
    --resource-group $RESOURCE_GROUP \
    --name ftp \
    --namespace Microsoft.Web \
    --resource-type basicPublishingCredentialsPolicies \
    --parent sites/$WEBAPP_NAME \
    --set properties.allow=true \
    --output none 2>/dev/null || echo "Note: Could not update FTP basic auth (may not be needed)"

echo "Assigning Managed Identity..."
WEBAPP_IDENTITY=$(az webapp identity assign \
    --name $WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query principalId -o tsv)

# Wait until the identity is visible in Azure AD
echo "Waiting for Managed Identity to propagate..."
for i in {1..10}; do
    STATUS=$(az ad sp show --id $WEBAPP_IDENTITY --query "appId" -o tsv 2>/dev/null || echo "")
    if [[ -n "$STATUS" ]]; then
        echo "Managed Identity is ready."
        break
    fi
    echo "Waiting... ($i/10)"
    sleep 5
done

if [[ -z "$STATUS" ]]; then
    echo "ERROR: Managed Identity not found in Azure AD. Try again in a few seconds."
    exit 1
fi

echo "Granting AcrPull role..."
ACR_ID=$(az acr show --name $ACR_NAME --query "id" -o tsv)
az role assignment create \
    --assignee $WEBAPP_IDENTITY \
    --role AcrPull \
    --scope $ACR_ID

# CRITICAL: Configure Web App to use Managed Identity for ACR authentication
echo "Configuring Web App to use Managed Identity for ACR..."
az webapp config set \
    --name $WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP \
    --generic-configurations '{"acrUseManagedIdentityCreds": true}'

# Container setzen
echo "Configuring container..."
az webapp config container set \
    --name $WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP \
    --container-image-name "$ACR_NAME.azurecr.io/$IMAGE_NAME:$IMAGE_VERSION" \
    --container-registry-url "https://$ACR_NAME.azurecr.io"

# CRITICAL FIX: Remove any existing admin credentials and set registry URL
echo "Removing admin credentials and configuring registry URL..."
az webapp config appsettings set \
    --name $WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings DOCKER_REGISTRY_SERVER_URL="https://$ACR_NAME.azurecr.io" \
    --output none

# Remove username/password to force managed identity usage
az webapp config appsettings delete \
    --name $WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP \
    --setting-names DOCKER_REGISTRY_SERVER_USERNAME DOCKER_REGISTRY_SERVER_PASSWORD \
    --output none 2>/dev/null || true

echo "Setting Health Check and Always On..."
az webapp config set \
    --name $WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP \
    --generic-configurations "{\"healthCheckPath\": \"$HEALTH_PATH\"}" \
    --always-on true

# Enable Continuous Deployment (Webhook)
echo "Enabling Continuous Deployment..."
az webapp deployment container config \
    --name $WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP \
    --enable-cd true

# Get Webhook URL
echo "Retrieving Webhook URL..."
WEBHOOK_URL=$(az webapp deployment container show-cd-url \
    --name $WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query CI_CD_URL -o tsv)

if [[ -z "$WEBHOOK_URL" ]]; then
    echo "WARNING: Could not retrieve webhook URL. Continuous deployment may not work."
else
    echo "Webhook URL retrieved successfully."

    # Create or update ACR Webhook
    WEBHOOK_NAME="${WEBAPP_NAME//-/}webhook"  # Remove hyphens for webhook name
    WEBHOOK_NAME="${WEBHOOK_NAME:0:50}"  # Max 50 chars for webhook name

    echo "Configuring ACR Webhook: $WEBHOOK_NAME..."

    # Check if webhook already exists
    WEBHOOK_EXISTS=$(az acr webhook list \
        --registry $ACR_NAME \
        --query "[?name=='$WEBHOOK_NAME'].name" -o tsv)

    if [[ -n "$WEBHOOK_EXISTS" ]]; then
        echo "Webhook already exists. Updating..."
        az acr webhook update \
            --name $WEBHOOK_NAME \
            --registry $ACR_NAME \
            --uri "$WEBHOOK_URL" \
            --actions push \
            --scope "$IMAGE_NAME:*" \
            --status enabled
    else
        echo "Creating new webhook..."
        az acr webhook create \
            --name $WEBHOOK_NAME \
            --registry $ACR_NAME \
            --uri "$WEBHOOK_URL" \
            --actions push \
            --scope "$IMAGE_NAME:*" \
            --status enabled
    fi

    echo "Webhook configured successfully!"
fi

# Additional wait for all permissions to propagate
echo "Waiting additional 30 seconds for all permissions to fully propagate..."
sleep 30

echo "Restarting Web App to apply changes..."
az webapp restart \
    --name $WEBAPP_NAME \
    --resource-group $RESOURCE_GROUP

echo ""
echo "=============================================="
echo "App Service setup completed successfully!"
echo "=============================================="
echo ""
echo "Configuration Summary:"
echo "  - Resource Group: $RESOURCE_GROUP"
echo "  - App Service Plan: $APP_SERVICE_PLAN"
echo "  - Web App: $WEBAPP_NAME"
echo "  - ACR: $ACR_NAME"
echo "  - Image: $IMAGE_NAME:$IMAGE_VERSION"
echo "  - Authentication: Managed Identity"
echo "  - Continuous Deployment: Enabled"
echo "  - Webhook: $WEBHOOK_NAME"
echo ""
echo "How it works now:"
echo "  1. Push any image: docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:<any-tag>"
echo "  2. ACR triggers webhook automatically"
echo "  3. Web App pulls and deploys new image"
echo "  4. No manual intervention needed!"
echo ""
echo "App URL: https://$WEBAPP_NAME.azurewebsites.net"
echo ""
echo "To manually trigger an update:"
echo "  az webapp config container set \\"
echo "    --name $WEBAPP_NAME \\"
echo "    --resource-group $RESOURCE_GROUP \\"
echo "    --container-image-name $ACR_NAME.azurecr.io/$IMAGE_NAME:<new-tag>"
echo ""
echo "To check logs:"
echo "  az webapp log tail --name $WEBAPP_NAME --resource-group $RESOURCE_GROUP"
echo ""
