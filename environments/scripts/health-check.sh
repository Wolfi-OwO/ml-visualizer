#!/bin/bash

# Health Check Script for ML Visualizer Environments
# Performs comprehensive health checks across all environments

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default values
TIMEOUT=30
VERBOSE=false
CHECK_ALL=false

# Functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Usage function
usage() {
    cat << EOF
Usage: $0 [OPTIONS] [ENVIRONMENT]

Health check script for ML Visualizer environments.

ENVIRONMENTS:
    testing     Check testing environment
    staging     Check staging environment
    production  Check production environment
    all         Check all environments

OPTIONS:
    -t, --timeout SECONDS    Request timeout (default: 30)
    -v, --verbose           Enable verbose output
    -h, --help              Show this help message

EXAMPLES:
    $0 production           # Check production environment
    $0 -v all               # Check all environments with verbose output
    $0 -t 60 staging        # Check staging with 60s timeout

ENVIRONMENT VARIABLES:
    AZURE_WEBAPP_NAME       Base name for production app service
EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            all)
                CHECK_ALL=true
                shift
                ;;
            testing|staging|production)
                ENVIRONMENT="$1"
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done

    if [[ -z "${ENVIRONMENT:-}" && "$CHECK_ALL" == "false" ]]; then
        log_error "Please specify an environment or use 'all'"
        usage
        exit 1
    fi
}

# Get environment URL
get_environment_url() {
    local env="$1"
    local base_name="${AZURE_WEBAPP_NAME:-ml-visualizer-app}"

    case $env in
        testing)
            echo "https://${base_name}-testing.azurewebsites.net"
            ;;
        staging)
            echo "https://${base_name}-staging.azurewebsites.net"
            ;;
        production)
            echo "https://${base_name}.azurewebsites.net"
            ;;
        *)
            log_error "Unknown environment: $env"
            return 1
            ;;
    esac
}

# Check HTTP response
check_http_response() {
    local url="$1"
    local env="$2"
    local result=0

    log_info "Checking HTTP response for $env environment..."

    if [[ "$VERBOSE" == "true" ]]; then
        log_info "URL: $url"
        log_info "Timeout: ${TIMEOUT}s"
    fi

    # Basic connectivity check
    local response_code
    response_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout "$TIMEOUT" --max-time "$TIMEOUT" "$url" || echo "000")

    if [[ "$response_code" == "200" ]]; then
        log_success "$env environment: HTTP $response_code"
    elif [[ "$response_code" == "000" ]]; then
        log_error "$env environment: Connection failed"
        result=1
    else
        log_warning "$env environment: HTTP $response_code"
        result=1
    fi

    return $result
}

# Check response time
check_response_time() {
    local url="$1"
    local env="$2"
    local result=0

    log_info "Measuring response time for $env environment..."

    local start_time end_time response_time
    start_time=$(date +%s.%N)

    if curl -s -o /dev/null --connect-timeout "$TIMEOUT" --max-time "$TIMEOUT" "$url" > /dev/null 2>&1; then
        end_time=$(date +%s.%N)
        response_time=$(echo "$end_time - $start_time" | bc)

        # Response time thresholds
        local threshold
        case $env in
            testing) threshold=10.0 ;;
            staging) threshold=5.0 ;;
            production) threshold=3.0 ;;
        esac

        if (( $(echo "$response_time <= $threshold" | bc -l) )); then
            log_success "$env environment: Response time ${response_time}s"
        else
            log_warning "$env environment: Slow response time ${response_time}s (>${threshold}s)"
            result=1
        fi

        if [[ "$VERBOSE" == "true" ]]; then
            log_info "Response time: ${response_time}s (threshold: ${threshold}s)"
        fi
    else
        log_error "$env environment: Response time check failed"
        result=1
    fi

    return $result
}

# Check SSL certificate
check_ssl_certificate() {
    local url="$1"
    local env="$2"
    local result=0

    log_info "Checking SSL certificate for $env environment..."

    local domain
    domain=$(echo "$url" | sed -e 's|^[^/]*//||' -e 's|/.*$||')

    if [[ "$VERBOSE" == "true" ]]; then
        log_info "Domain: $domain"
    fi

    # Check certificate expiry
    local cert_info
    if cert_info=$(echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null); then
        local expiry_date
        expiry_date=$(echo "$cert_info" | grep "notAfter" | cut -d= -f2)
        local expiry_timestamp
        expiry_timestamp=$(date -d "$expiry_date" +%s)
        local current_timestamp
        current_timestamp=$(date +%s)
        local days_until_expiry
        days_until_expiry=$(( (expiry_timestamp - current_timestamp) / 86400 ))

        if [[ $days_until_expiry -gt 30 ]]; then
            log_success "$env environment: SSL certificate valid (expires in ${days_until_expiry} days)"
        elif [[ $days_until_expiry -gt 7 ]]; then
            log_warning "$env environment: SSL certificate expires soon (${days_until_expiry} days)"
            result=1
        else
            log_error "$env environment: SSL certificate expires very soon (${days_until_expiry} days)"
            result=1
        fi

        if [[ "$VERBOSE" == "true" ]]; then
            log_info "Certificate expires: $expiry_date"
        fi
    else
        log_error "$env environment: SSL certificate check failed"
        result=1
    fi

    return $result
}

# Check application health endpoint
check_application_health() {
    local url="$1"
    local env="$2"
    local result=0

    log_info "Checking application health for $env environment..."

    # Check if health endpoint exists (optional)
    local health_url="${url}/health"
    local response_code
    response_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout "$TIMEOUT" --max-time "$TIMEOUT" "$health_url" || echo "000")

    case $response_code in
        200)
            log_success "$env environment: Health endpoint responding"
            ;;
        404)
            log_info "$env environment: No health endpoint (optional)"
            ;;
        *)
            log_warning "$env environment: Health endpoint issue (HTTP $response_code)"
            ;;
    esac

    # Check main application response
    if curl -s --connect-timeout "$TIMEOUT" --max-time "$TIMEOUT" "$url" | grep -q "ML Visualizer\|Streamlit\|Data Science" 2>/dev/null; then
        log_success "$env environment: Application content verified"
    else
        log_warning "$env environment: Application content check failed"
        result=1
    fi

    return $result
}

# Comprehensive health check for a single environment
check_environment() {
    local env="$1"
    local url
    local overall_result=0

    echo
    echo "======================================"
    echo "Health Check: ${env^^} Environment"
    echo "======================================"

    url=$(get_environment_url "$env")
    if [[ $? -ne 0 ]]; then
        return 1
    fi

    if [[ "$VERBOSE" == "true" ]]; then
        log_info "Starting health check for $env environment"
        log_info "Target URL: $url"
        echo
    fi

    # Run all health checks
    check_http_response "$url" "$env" || overall_result=1
    check_response_time "$url" "$env" || overall_result=1
    check_ssl_certificate "$url" "$env" || overall_result=1
    check_application_health "$url" "$env" || overall_result=1

    echo
    if [[ $overall_result -eq 0 ]]; then
        log_success "${env^^} environment: All checks passed!"
    else
        log_error "${env^^} environment: Some checks failed"
    fi

    return $overall_result
}

# Main function
main() {
    local overall_result=0

    echo "ML Visualizer Environment Health Check"
    echo "=========================================="

    # Check prerequisites
    if ! command -v curl &> /dev/null; then
        log_error "curl is required but not installed"
        exit 1
    fi

    if ! command -v bc &> /dev/null; then
        log_error "bc is required but not installed"
        exit 1
    fi

    if ! command -v openssl &> /dev/null; then
        log_warning "openssl not found - SSL certificate checks will be skipped"
    fi

    if [[ "$CHECK_ALL" == "true" ]]; then
        log_info "Performing health checks on all environments"

        for env in testing staging production; do
            check_environment "$env" || overall_result=1
        done
    else
        check_environment "$ENVIRONMENT" || overall_result=1
    fi

    echo
    echo "========================================"
    if [[ $overall_result -eq 0 ]]; then
        log_success "All health checks completed successfully!"
    else
        log_error "Some health checks failed - please investigate"
    fi
    echo "========================================"

    exit $overall_result
}

# Script execution
parse_args "$@"
main
