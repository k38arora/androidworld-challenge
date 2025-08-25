#!/bin/bash

# AndroidWorld Load Testing Script
# Runs k6 load tests against the AndroidWorld worker service

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEFAULT_BASE_URL="http://localhost:8080"
DEFAULT_DURATION="23m"
DEFAULT_OUTPUT_DIR="$PROJECT_ROOT/load-testing/results"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  AndroidWorld Load Testing${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    print_info "Checking dependencies..."
    
    # Check if k6 is installed
    if ! command -v k6 &> /dev/null; then
        print_error "k6 is not installed. Please install it first:"
        echo "  macOS: brew install k6"
        echo "  Ubuntu: sudo apt-get install k6"
        echo "  Or download from: https://k6.io/docs/getting-started/installation/"
        exit 1
    fi
    
    # Check k6 version
    K6_VERSION=$(k6 version | head -n1)
    print_info "Using k6: $K6_VERSION"
    
    # Check if Docker is running (if testing against containerized service)
    if docker info &> /dev/null; then
        print_info "Docker is running"
    else
        print_warning "Docker is not running - make sure your service is accessible"
    fi
}

check_service_health() {
    local base_url=$1
    
    print_info "Checking service health at $base_url..."
    
    # Try to connect to health endpoint
    if curl -f -s "$base_url/health" > /dev/null; then
        print_info "Service is healthy"
        return 0
    else
        print_error "Service is not accessible at $base_url/health"
        return 1
    fi
}

run_load_test() {
    local base_url=$1
    local duration=$2
    local output_dir=$3
    
    print_info "Starting load test..."
    print_info "Target URL: $base_url"
    print_info "Test duration: $duration"
    print_info "Output directory: $output_dir"
    
    # Create output directory
    mkdir -p "$output_dir"
    
    # Generate timestamp for this test run
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    OUTPUT_FILE="$output_dir/load_test_$TIMESTAMP.json"
    SUMMARY_FILE="$output_dir/load_test_$TIMESTAMP_summary.txt"
    
    print_info "Running k6 load test..."
    
    # Run k6 with environment variables and output options
    k6 run \
        --env BASE_URL="$base_url" \
        --out json="$OUTPUT_FILE" \
        --out influxdb=http://localhost:8086/k6 \
        --summary-export="$SUMMARY_FILE" \
        --tag environment=production \
        --tag test_type=load_test \
        --tag service=androidworld-worker \
        "$SCRIPT_DIR/k6-load-test.js"
    
    if [ $? -eq 0 ]; then
        print_info "Load test completed successfully"
        print_info "Results saved to: $OUTPUT_FILE"
        print_info "Summary saved to: $SUMMARY_FILE"
    else
        print_error "Load test failed"
        exit 1
    fi
}

generate_report() {
    local output_dir=$1
    local timestamp=$2
    
    print_info "Generating load test report..."
    
    REPORT_FILE="$output_dir/load_test_${timestamp}_report.md"
    
    cat > "$REPORT_FILE" << EOF
# AndroidWorld Load Test Report

**Test Date:** $(date)
**Test Duration:** $DEFAULT_DURATION
**Target Service:** AndroidWorld Worker

## Test Configuration

- **Load Test Tool:** k6
- **Test Script:** k6-load-test.js
- **Stages:**
  - 0-2m: Ramp up to 10 users
  - 2-5m: Stay at 10 users
  - 5-8m: Ramp up to 50 users
  - 8-13m: Stay at 50 users
  - 13-16m: Ramp up to 100 users
  - 16-21m: Stay at 100 users
  - 21-23m: Ramp down to 0 users

## Performance Thresholds

- 95% of requests must complete within 5 seconds
- 99% of requests must complete within 10 seconds
- Error rate must be less than 5%
- Task success rate must be above 90%

## Results Summary

Results are available in the following files:
- **Raw Data:** load_test_${timestamp}.json
- **Summary:** load_test_${timestamp}_summary.txt

## Analysis

### Key Metrics

1. **Response Time:**
   - Average response time
   - 95th percentile response time
   - 99th percentile response time

2. **Throughput:**
   - Requests per second
   - Concurrent users supported

3. **Reliability:**
   - Error rate
   - Task success rate
   - Availability

### Recommendations

Based on the test results, consider the following:

1. **Scaling:**
   - Current capacity vs. expected load
   - Horizontal scaling requirements
   - Resource optimization

2. **Performance:**
   - Bottleneck identification
   - Response time optimization
   - Caching strategies

3. **Monitoring:**
   - Key performance indicators
   - Alerting thresholds
   - Observability improvements

## Next Steps

1. Analyze detailed results in the JSON output file
2. Review system performance under different load levels
3. Implement performance improvements based on findings
4. Schedule regular load testing as part of CI/CD pipeline

---

*Report generated automatically by AndroidWorld Load Testing Suite*
EOF

    print_info "Report generated: $REPORT_FILE"
}

# Main execution
main() {
    print_header
    
    # Parse command line arguments
    BASE_URL="${1:-$DEFAULT_BASE_URL}"
    DURATION="${2:-$DEFAULT_DURATION}"
    OUTPUT_DIR="${3:-$DEFAULT_OUTPUT_DIR}"
    
    print_info "Configuration:"
    echo "  Base URL: $BASE_URL"
    echo "  Duration: $DURATION"
    echo "  Output Directory: $OUTPUT_DIR"
    echo ""
    
    # Check dependencies
    check_dependencies
    
    # Check service health
    if ! check_service_health "$BASE_URL"; then
        print_error "Cannot proceed with load test - service is not healthy"
        exit 1
    fi
    
    # Run load test
    run_load_test "$BASE_URL" "$DURATION" "$OUTPUT_DIR"
    
    # Generate report
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    generate_report "$OUTPUT_DIR" "$TIMESTAMP"
    
    print_info "Load testing completed successfully!"
    print_info "Check the results directory for detailed output and reports."
}

# Show usage if help is requested
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "Usage: $0 [BASE_URL] [DURATION] [OUTPUT_DIR]"
    echo ""
    echo "Arguments:"
    echo "  BASE_URL     Target service URL (default: $DEFAULT_BASE_URL)"
    echo "  DURATION     Test duration (default: $DEFAULT_DURATION)"
    echo "  OUTPUT_DIR   Output directory (default: $DEFAULT_OUTPUT_DIR)"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Use all defaults"
    echo "  $0 http://localhost:8080              # Custom base URL"
    echo "  $0 http://localhost:8080 10m         # Custom duration"
    echo "  $0 http://localhost:8080 10m ./results # Custom output directory"
    exit 0
fi

# Run main function
main "$@"
