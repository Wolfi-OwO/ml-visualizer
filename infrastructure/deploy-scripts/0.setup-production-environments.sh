#!/usr/bin/env bash

# Container Apps focused production environment setup
# Usage example:
# ./0.setup-production-environments.sh --resource-group dsai-5bhif-webapp --location northeurope --acr dsaiwebappacr01 --env quizapp-env --app dsai-containerapp --image-tag 1.0.5 --min-replicas 0 --max-replicas 30 --subscription <sub-id>

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info(){ echo -e "${BLUE}[INFO]${NC} $1"; }
log_success(){ echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning(){ echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error(){ echo -e "${RED}[ERROR]${NC} $1"; }

parse_args(){
    # Defaults
    LOCATION="northeurope"
    AZURE_CONTAINERAPP_ENV_NAME="ca-env"
    AZURE_CONTAINERAPP_NAME="ml-visualizer"
    IMAGE_TAG="latest"
    MIN_REPLICAS=0
    MAX_REPLICAS=30

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --resource-group|-g)
                AZURE_RESOURCE_GROUP="$2"; shift 2;;
            --location|-l)
                LOCATION="$2"; shift 2;;
            else
            # If we have admin creds, pass registry params so Container App knows it's a private registry
            if [[ -n "${ACR_ADMIN_USERNAME:-}" && -n "${ACR_ADMIN_PASSWORD:-}" ]]; then
                log_info "Creating container app with registry credentials"
                az containerapp create \
                    --name "$app_name" \
                    --resource-group "$AZURE_RESOURCE_GROUP" \
                    --environment "$env_name" \
                    --image "$image" \
                    --ingress external \
                    --target-port 8501 \
                    --cpu 0.5 \
                    --memory 1Gi \
                    --env-vars ENVIRONMENT=production VERSION="$image_tag" PORT=8501 \
                    --registry-server "${ACR_NAME}.azurecr.io" \
                    --registry-username "$ACR_ADMIN_USERNAME" \
                    --registry-password "$ACR_ADMIN_PASSWORD" >/dev/null
                log_success "Container App created (private registry configured)"
            else
                az containerapp create \
                    --name "$app_name" \
                    --resource-group "$AZURE_RESOURCE_GROUP" \
                    --environment "$env_name" \
                    --image "$image" \
                    --ingress external \
                    --target-port 8501 \
                    --cpu 0.5 \
                    --memory 1Gi \
                    --env-vars ENVIRONMENT=production VERSION="$image_tag" PORT=8501 >/dev/null
                log_success "Container App created"
            fi
        fi
    done
}

check_prereqs(){
    local req=("AZURE_SUBSCRIPTION_ID" "AZURE_RESOURCE_GROUP" "ACR_NAME")
    local miss=()
    for v in "${req[@]}"; do
        if [[ -z "${!v:-}" ]]; then
            miss+=("$v")
        fi
    done
    if [[ ${#miss[@]} -gt 0 ]]; then
        log_error "Missing required inputs: ${miss[*]}"
        echo
        echo "Please export the following before running:"
        for v in "${req[@]}"; do
            echo "  export $v=..."
        done
        echo "Or supply them via flags: --resource-group, --acr, --subscription"
        exit 1
    fi

    if ! command -v az &> /dev/null; then
        log_error "Azure CLI (az) not found"
        exit 1
    fi
    if ! command -v jq &> /dev/null; then
        log_error "jq is required (https://stedolan.github.io/jq/)"
        exit 1
    fi

    if ! az account show &> /dev/null; then
        log_error "Not logged into Azure CLI. Run: az login"
        exit 1
    fi
    log_success "Prerequisites OK"
}

set_subscription(){
    log_info "Setting subscription $AZURE_SUBSCRIPTION_ID"
    az account set --subscription "$AZURE_SUBSCRIPTION_ID"
}

ensure_rg(){
    if az group show --name "$AZURE_RESOURCE_GROUP" &> /dev/null; then
        log_info "Resource group $AZURE_RESOURCE_GROUP exists"
    else
        log_info "Creating resource group $AZURE_RESOURCE_GROUP"
        az group create --name "$AZURE_RESOURCE_GROUP" --location "$LOCATION" >/dev/null
        log_success "RG created"
    fi
}

ensure_log_analytics(){
    LAW_NAME="${AZURE_CONTAINERAPP_ENV_NAME}-law"
    if az monitor log-analytics workspace show --resource-group "$AZURE_RESOURCE_GROUP" --workspace-name "$LAW_NAME" &> /dev/null; then
        log_info "Log Analytics workspace $LAW_NAME exists"
    else
        log_info "Creating Log Analytics workspace $LAW_NAME"
        az monitor log-analytics workspace create \
            --resource-group "$AZURE_RESOURCE_GROUP" \
            --workspace-name "$LAW_NAME" \
            --location "$LOCATION" \
            --sku PerGB2018 >/dev/null
        log_success "Log Analytics created"
    fi
    echo "$LAW_NAME"
}

ensure_containerapps_env(){
    local env_name="$AZURE_CONTAINERAPP_ENV_NAME"
        if az containerapp env show --name "$env_name" --resource-group "$AZURE_RESOURCE_GROUP" &> /dev/null; then
            log_info "Container Apps environment $env_name exists"
        else
            log_info "Creating Container Apps environment $env_name (no Log Analytics binding)"
            az containerapp env create \
                --name "$env_name" \
                --resource-group "$AZURE_RESOURCE_GROUP" \
                --location "$LOCATION" >/dev/null
            log_success "Container Apps environment created"
        fi
    echo "$env_name"
}

ensure_acr(){
    if az acr show --name "$ACR_NAME" --resource-group "$AZURE_RESOURCE_GROUP" &> /dev/null; then
        log_info "ACR $ACR_NAME exists"
        # Try to fetch admin credentials if admin enabled
        local ac_user ac_pass
        ac_user=$(az acr credential show --name "$ACR_NAME" --query username -o tsv 2>/dev/null || true)
        ac_pass=$(az acr credential show --name "$ACR_NAME" --query passwords[0].value -o tsv 2>/dev/null || true)
        if [[ -n "$ac_user" && -n "$ac_pass" && "$ac_pass" != "null" ]]; then
            ACR_ADMIN_USERNAME="$ac_user"
            ACR_ADMIN_PASSWORD="$ac_pass"
            export ACR_ADMIN_USERNAME ACR_ADMIN_PASSWORD
            log_info "Fetched existing ACR admin credentials"
        else
            log_warning "ACR exists but admin credentials not available (admin may be disabled)."
        fi
        return 0
    fi

    log_warning "ACR '$ACR_NAME' not found in resource group '$AZURE_RESOURCE_GROUP'."
    read -r -p "Create ACR '$ACR_NAME' in '$AZURE_RESOURCE_GROUP'? (y/N): " create_acr
    if [[ "$create_acr" =~ ^[Yy]$ ]]; then
        log_info "Creating ACR $ACR_NAME (Basic, admin enabled)"
        az acr create --resource-group "$AZURE_RESOURCE_GROUP" --name "$ACR_NAME" --sku Basic --admin-enabled true >/dev/null
        log_success "ACR created"
        # Print admin credentials for user to copy into CI if desired
        local ac_user ac_pass
        ac_user=$(az acr credential show --name "$ACR_NAME" --query username -o tsv)
        ac_pass=$(az acr credential show --name "$ACR_NAME" --query passwords[0].value -o tsv)
        echo
        log_success "ACR admin credentials (store securely)"
        echo "ACR_LOGIN_SERVER=${ACR_NAME}.azurecr.io"
        echo "ACR_ADMIN_USERNAME=$ac_user"
        echo "ACR_ADMIN_PASSWORD=$ac_pass"
        echo
        # export for later wiring into container app
        ACR_ADMIN_USERNAME="$ac_user"
        ACR_ADMIN_PASSWORD="$ac_pass"
        export ACR_ADMIN_USERNAME ACR_ADMIN_PASSWORD
        return 0
    else
        log_error "ACR not available. Please create the ACR or set --acr to an existing registry."
        exit 1
    fi
}

configure_containerapp_registry(){
    local app_name="$1"
    local server="${ACR_NAME}.azurecr.io"
    if [[ -z "${ACR_ADMIN_USERNAME:-}" || -z "${ACR_ADMIN_PASSWORD:-}" ]]; then
        log_warning "No ACR admin credentials available to wire into Container App"
        return 0
    fi

    log_info "Configuring Container App to use ACR admin credentials"
    # Try CLI flags (if supported), otherwise use JSON patch via --set
    if az containerapp update --name "$app_name" --resource-group "$AZURE_RESOURCE_GROUP" --registry-server "$server" --registry-username "$ACR_ADMIN_USERNAME" --registry-password "$ACR_ADMIN_PASSWORD" >/dev/null 2>&1; then
        log_success "Wired registry credentials via CLI flags"
        return 0
    fi

    # Fallback: set configuration.registries JSON
    local registries_json
    registries_json=$(jq -n --arg s "$server" --arg u "$ACR_ADMIN_USERNAME" --arg p "$ACR_ADMIN_PASSWORD" '[{server:$s,username:$u,password:$p}]')
    if az containerapp update --name "$app_name" --resource-group "$AZURE_RESOURCE_GROUP" --set "configuration.registries=$registries_json" >/dev/null 2>&1; then
        log_success "Wired registry credentials via configuration.registries"
        return 0
    fi

    log_warning "Failed to wire registry credentials into Container App automatically. You may need to configure registry credentials manually."
}

ensure_containerapp_image(){
    local app_name="$1"
    local image="${ACR_NAME}.azurecr.io/ml-visualizer:${IMAGE_TAG}"
    log_info "Ensuring Container App image is set to $image"
    if az containerapp update --name "$app_name" --resource-group "$AZURE_RESOURCE_GROUP" --image "$image" >/dev/null 2>&1; then
        log_success "Container App image set to $image"
    else
        log_warning "Failed to set Container App image to $image"
    fi
}

create_container_app(){
    local app_name="$AZURE_CONTAINERAPP_NAME"
    local env_name="$AZURE_CONTAINERAPP_ENV_NAME"
    local image_tag="$IMAGE_TAG"
    local image="${ACR_NAME}.azurecr.io/ml-visualizer:${image_tag}"

    log_info "Creating/updating Container App $app_name (image=$image)"
    if az containerapp show --name "$app_name" --resource-group "$AZURE_RESOURCE_GROUP" &> /dev/null; then
        log_info "Container App exists — updating image"
        az containerapp update --name "$app_name" --resource-group "$AZURE_RESOURCE_GROUP" --image "$image" >/dev/null
        else
        az containerapp create \
            --name "$app_name" \
            --resource-group "$AZURE_RESOURCE_GROUP" \
            --environment "$env_name" \
            --image "$image" \
            --ingress external \
            --target-port 8501 \
            --cpu 0.5 \
            --memory 1Gi \
            --env-vars ENVIRONMENT=production VERSION="$image_tag" PORT=8501 >/dev/null
        log_success "Container App created"
    fi

    # Set scale settings (min/max replicas)
    log_info "Applying scale: min=$MIN_REPLICAS max=$MAX_REPLICAS"
    az containerapp update --name "$app_name" --resource-group "$AZURE_RESOURCE_GROUP" \
        --set configuration.scale.minReplicas="$MIN_REPLICAS" --set configuration.scale.maxReplicas="$MAX_REPLICAS" >/dev/null || log_warning "Failed to set scale values (CLI may not support)."

    # Return app name
    echo "$app_name"
}

create_ci_sp_and_print_vars(){
    local sp_name="ml-visualizer-cicd-sp"
    log_info "Creating (or fetching) service principal: $sp_name"
    local existing
    existing=$(az ad sp list --display-name "$sp_name" --query '[0].appId' -o tsv 2>/dev/null || true)
    local sp_output
    if [[ -n "$existing" && "$existing" != "null" ]]; then
        log_info "Service principal exists: $existing"
        read -r -p "Use existing SP ($existing)? (Y/n): " use_existing
        if [[ "$use_existing" =~ ^[Nn]$ ]]; then
            log_info "Creating new service principal"
            sp_output=$(az ad sp create-for-rbac --name "$sp_name" --role Contributor --scopes "/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/$AZURE_RESOURCE_GROUP" --sdk-auth)
        else
            log_info "Creating credential for existing SP"
            sp_output=$(az ad app credential reset --id "$existing" --append --years 2)
            sp_output=$(jq -n --arg clientId "$existing" --arg clientSecret "REPLACE_ME" --arg tenantId "$(az account show --query tenantId -o tsv)" '{clientId:$clientId,clientSecret:$clientSecret,tenantId:$tenantId}')
        fi
    else
        sp_output=$(az ad sp create-for-rbac --name "$sp_name" --role Contributor --scopes "/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/$AZURE_RESOURCE_GROUP" --sdk-auth)
    fi

    # Parse SDK auth to extract clientId/clientSecret/tenantId
    local client_id client_secret tenant_id
    client_id=$(echo "$sp_output" | jq -r '.clientId')
    client_secret=$(echo "$sp_output" | jq -r '.clientSecret')
    tenant_id=$(echo "$sp_output" | jq -r '.tenantId')

    # Assign ACR roles to the SP so CI can push images
    local acr_scope="/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/$AZURE_RESOURCE_GROUP/providers/Microsoft.ContainerRegistry/registries/$ACR_NAME"
    log_info "Granting AcrPush/AcrPull to SP"
    az role assignment create --assignee "$client_id" --role AcrPull --scope "$acr_scope" >/dev/null || true
    az role assignment create --assignee "$client_id" --role AcrPush --scope "$acr_scope" >/dev/null || true

    # Print variables for GitLab
    echo
    log_success "==== GitLab CI/CD variables to set (copy these) ===="
    echo "AZURE_SUBSCRIPTION_ID=$AZURE_SUBSCRIPTION_ID"
    echo "AZURE_RESOURCE_GROUP=$AZURE_RESOURCE_GROUP"
    echo "ACR_NAME=$ACR_NAME"
    echo "ACR_LOGIN_SERVER=${ACR_NAME}.azurecr.io"
    echo "AZURE_CONTAINERAPP_ENV_NAME=${AZURE_CONTAINERAPP_ENV_NAME}"
    echo "AZURE_CONTAINERAPP_NAME=${AZURE_CONTAINERAPP_NAME}"
    echo "IMAGE_TAG=${IMAGE_TAG}"
    echo "MIN_REPLICAS=${MIN_REPLICAS}"
    echo "MAX_REPLICAS=${MAX_REPLICAS}"
    echo "AZURE_CLIENT_ID=$client_id"
    echo "AZURE_CLIENT_SECRET=$client_secret"
    echo "AZURE_TENANT_ID=$tenant_id"
    echo "AZURE_CI_SDK_AUTH=$sp_output"
    echo "Note: mark AZURE_CLIENT_SECRET and AZURE_CI_SDK_AUTH as masked/protected"
    echo
}

main(){
    parse_args "$@"
    check_prereqs
    set_subscription
    ensure_rg
    ensure_acr
    ensure_containerapps_env >/dev/null
    APP_NAME=$(create_container_app)
    # If we have ACR admin creds from ensure_acr, configure the container app to use them
    configure_containerapp_registry "$APP_NAME"
    # Re-apply image after wiring registry credentials to force a pull from ACR
    ensure_containerapp_image "$APP_NAME"
    create_ci_sp_and_print_vars
    log_success "Done. Container App: $APP_NAME"
}

main "$@"
