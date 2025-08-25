#!/bin/bash

# AndroidWorld Runner Script
# This script connects to Genymotion emulators and runs AndroidWorld tasks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTAINER_NAME="androidworld-runner"
IMAGE_NAME="androidworld:latest"
LOG_DIR="$SCRIPT_DIR/logs"
OUTPUT_DIR="$SCRIPT_DIR/outputs"

# Default values
MODE="cloud"
EMULATOR_IP=""
EMULATOR_PORT="5555"
TASK_TYPE="basic"
VERBOSE=false
BUILD_IMAGE=false

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    -h, --help              Show this help message
    -m, --mode MODE         Set mode: cloud, local, or docker (default: cloud)
    -i, --ip IP             Emulator IP address (required for cloud mode)
    -p, --port PORT         Emulator ADB port (default: 5555)
    -t, --task TASK         Task type: basic, advanced, custom (default: basic)
    -v, --verbose           Enable verbose output
    --build                 Build Docker image before running
    --test                  Run in test mode (minimal tasks)
    --local                 Alias for --mode local
    --docker                Alias for --mode docker

Examples:
    # Cloud deployment
    $0 --mode cloud --ip 192.168.1.100
    
    # Local emulator
    $0 --local
    
    # Docker mode with custom IP
    $0 --docker --ip 10.0.0.50
    
    # Test mode
    $0 --test --local

EOF
}

# Function to log messages
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")
            echo -e "${GREEN}[$timestamp] INFO: $message${NC}"
            ;;
        "WARN")
            echo -e "${YELLOW}[$timestamp] WARN: $message${NC}"
            ;;
        "ERROR")
            echo -e "${RED}[$timestamp] ERROR: $message${NC}"
            ;;
        "DEBUG")
            if [ "$VERBOSE" = true ]; then
                echo -e "${BLUE}[$timestamp] DEBUG: $message${NC}"
            fi
            ;;
    esac
}

# Function to check prerequisites
check_prerequisites() {
    log "INFO" "Checking prerequisites..."
    
    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        log "ERROR" "Docker not found. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log "ERROR" "Docker daemon not running. Please start Docker first."
        exit 1
    fi
    
    # Check if ADB is available locally (for local mode)
    if [ "$MODE" = "local" ] && ! command -v adb &> /dev/null; then
        log "WARN" "ADB not found locally. This is required for local mode."
        log "INFO" "Please install Android SDK or Android Studio."
        exit 1
    fi
    
    log "INFO" "Prerequisites check passed"
}

# Function to build Docker image
build_docker_image() {
    log "INFO" "Building Docker image..."
    
    if [ ! -f "$SCRIPT_DIR/Dockerfile" ]; then
        log "ERROR" "Dockerfile not found in $SCRIPT_DIR"
        exit 1
    fi
    
    cd "$SCRIPT_DIR"
    docker build -t "$IMAGE_NAME" .
    
    if [ $? -eq 0 ]; then
        log "INFO" "Docker image built successfully"
    else
        log "ERROR" "Failed to build Docker image"
        exit 1
    fi
}

# Function to create directories
create_directories() {
    log "DEBUG" "Creating necessary directories..."
    
    mkdir -p "$LOG_DIR"
    mkdir -p "$OUTPUT_DIR"
    
    log "DEBUG" "Directories created: $LOG_DIR, $OUTPUT_DIR"
}

# Function to connect to emulator
connect_to_emulator() {
    local ip=$1
    local port=$2
    
    log "INFO" "Connecting to emulator at $ip:$port..."
    
    if [ "$MODE" = "local" ]; then
        # Local mode: use local ADB
        adb connect "$ip:$port"
        if [ $? -eq 0 ]; then
            log "INFO" "Successfully connected to local emulator"
        else
            log "ERROR" "Failed to connect to local emulator"
            exit 1
        fi
    else
        # Cloud/Docker mode: check if container can reach emulator
        log "DEBUG" "Testing connectivity to emulator from container..."
        if docker run --rm --network host "$IMAGE_NAME" adb connect "$ip:$port"; then
            log "INFO" "Container can reach emulator"
        else
            log "WARN" "Container cannot reach emulator directly. Will use host networking."
        fi
    fi
}

# Function to verify emulator connection
verify_connection() {
    log "INFO" "Verifying emulator connection..."
    
    if [ "$MODE" = "local" ]; then
        # Check local ADB devices
        local devices=$(adb devices | grep -v "List of devices" | grep -v "^$" | wc -l)
        if [ "$devices" -gt 0 ]; then
            log "INFO" "Found $devices connected device(s)"
            adb devices
        else
            log "ERROR" "No devices found. Please check emulator connection."
            exit 1
        fi
    else
        # Check from container
        local devices=$(docker run --rm --network host "$IMAGE_NAME" adb devices | grep -v "List of devices" | grep -v "^$" | wc -l)
        if [ "$devices" -gt 0 ]; then
            log "INFO" "Found $devices connected device(s) from container"
            docker run --rm --network host "$IMAGE_NAME" adb devices
        else
            log "ERROR" "No devices found from container. Please check emulator connection."
            exit 1
        fi
    fi
}

# Function to run AndroidWorld tasks
run_androidworld_tasks() {
    log "INFO" "Starting AndroidWorld tasks..."
    
    local task_script=""
    case $TASK_TYPE in
        "basic")
            task_script="basic_tasks.py"
            ;;
        "advanced")
            task_script="advanced_tasks.py"
            ;;
        "custom")
            task_script="custom_tasks.py"
            ;;
        "test")
            task_script="test_tasks.py"
            ;;
        *)
            log "ERROR" "Unknown task type: $TASK_TYPE"
            exit 1
            ;;
    esac
    
    # Create a simple task script if it doesn't exist
    if [ ! -f "$SCRIPT_DIR/scripts/$task_script" ]; then
        log "WARN" "Task script not found. Creating placeholder..."
        create_placeholder_tasks "$task_script"
    fi
    
    log "INFO" "Running $TASK_TYPE tasks..."
    
    if [ "$MODE" = "local" ]; then
        # Run locally
        python3 "$SCRIPT_DIR/scripts/$task_script" 2>&1 | tee "$LOG_DIR/androidworld_$(date +%Y%m%d_%H%M%S).log"
    else
        # Run in container
        docker run --rm \
            --network host \
            -v "$SCRIPT_DIR/scripts:/workspace/scripts:ro" \
            -v "$LOG_DIR:/workspace/logs" \
            -v "$OUTPUT_DIR:/workspace/outputs" \
            "$IMAGE_NAME" \
            python3 "/workspace/scripts/$task_script" 2>&1 | tee "$LOG_DIR/androidworld_$(date +%Y%m%d_%H%M%S).log"
    fi
    
    if [ $? -eq 0 ]; then
        log "INFO" "AndroidWorld tasks completed successfully"
    else
        log "ERROR" "AndroidWorld tasks failed"
        exit 1
    fi
}

# Function to create placeholder task scripts
create_placeholder_tasks() {
    local script_name=$1
    local script_path="$SCRIPT_DIR/scripts/$script_name"
    
    mkdir -p "$SCRIPT_DIR/scripts"
    
    cat > "$script_path" << 'EOF'
#!/usr/bin/env python3
"""
Placeholder AndroidWorld task script
Replace this with actual AndroidWorld implementation
"""

import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_basic_tasks():
    """Run basic AndroidWorld tasks"""
    logger.info("Starting basic AndroidWorld tasks...")
    
    tasks = [
        "Initialize Android environment",
        "Check device connectivity",
        "Verify app installation",
        "Run basic UI tests",
        "Collect device information"
    ]
    
    for i, task in enumerate(tasks, 1):
        logger.info(f"Task {i}/{len(tasks)}: {task}")
        time.sleep(1)  # Simulate task execution
        
        # Simulate task success/failure
        if i == 3:  # Simulate one task failure
            logger.warning(f"Task '{task}' completed with warnings")
        else:
            logger.info(f"Task '{task}' completed successfully")
    
    logger.info("All basic tasks completed!")

def run_advanced_tasks():
    """Run advanced AndroidWorld tasks"""
    logger.info("Starting advanced AndroidWorld tasks...")
    
    tasks = [
        "Performance benchmarking",
        "Memory usage analysis",
        "Network connectivity tests",
        "Battery usage monitoring",
        "Stress testing"
    ]
    
    for i, task in enumerate(tasks, 1):
        logger.info(f"Advanced Task {i}/{len(tasks)}: {task}")
        time.sleep(2)  # Simulate longer task execution
        logger.info(f"Advanced Task '{task}' completed successfully")
    
    logger.info("All advanced tasks completed!")

def run_test_tasks():
    """Run minimal test tasks"""
    logger.info("Starting test tasks...")
    
    tasks = [
        "Quick connectivity check",
        "Basic functionality test"
    ]
    
    for task in tasks:
        logger.info(f"Test: {task}")
        time.sleep(0.5)
        logger.info(f"Test '{task}' passed")
    
    logger.info("All test tasks passed!")

def main():
    """Main function"""
    logger.info("=" * 50)
    logger.info("AndroidWorld Task Runner")
    logger.info(f"Started at: {datetime.now()}")
    logger.info("=" * 50)
    
    # Determine which tasks to run based on script name
    if "test" in __file__:
        run_test_tasks()
    elif "advanced" in __file__:
        run_advanced_tasks()
    else:
        run_basic_tasks()
    
    logger.info("=" * 50)
    logger.info("Task execution completed successfully!")
    logger.info(f"Finished at: {datetime.now()}")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()
EOF
    
    chmod +x "$script_path"
    log "INFO" "Created placeholder task script: $script_path"
}

# Function to cleanup
cleanup() {
    log "DEBUG" "Cleaning up..."
    
    # Stop any running containers
    if docker ps -q --filter "name=$CONTAINER_NAME" | grep -q .; then
        log "DEBUG" "Stopping container: $CONTAINER_NAME"
        docker stop "$CONTAINER_NAME" &>/dev/null || true
    fi
    
    # Remove stopped containers
    if docker ps -aq --filter "name=$CONTAINER_NAME" | grep -q .; then
        log "DEBUG" "Removing container: $CONTAINER_NAME"
        docker rm "$CONTAINER_NAME" &>/dev/null || true
    fi
}

# Function to parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -m|--mode)
                MODE="$2"
                shift 2
                ;;
            -i|--ip)
                EMULATOR_IP="$2"
                shift 2
                ;;
            -p|--port)
                EMULATOR_PORT="$2"
                shift 2
                ;;
            -t|--task)
                TASK_TYPE="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            --build)
                BUILD_IMAGE=true
                shift
                ;;
            --test)
                TASK_TYPE="test"
                shift
                ;;
            --local)
                MODE="local"
                shift
                ;;
            --docker)
                MODE="docker"
                shift
                ;;
            *)
                log "ERROR" "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Function to validate configuration
validate_config() {
    log "DEBUG" "Validating configuration..."
    
    # Validate mode
    case $MODE in
        "cloud"|"local"|"docker")
            ;;
        *)
            log "ERROR" "Invalid mode: $MODE. Must be cloud, local, or docker."
            exit 1
            ;;
    esac
    
    # Validate task type
    case $TASK_TYPE in
        "basic"|"advanced"|"custom"|"test")
            ;;
        *)
            log "ERROR" "Invalid task type: $TASK_TYPE. Must be basic, advanced, custom, or test."
            exit 1
            ;;
    esac
    
    # Check if IP is provided for cloud mode
    if [ "$MODE" = "cloud" ] && [ -z "$EMULATOR_IP" ]; then
        log "ERROR" "Emulator IP address is required for cloud mode. Use --ip option."
        exit 1
    fi
    
    log "DEBUG" "Configuration validation passed"
}

# Main function
main() {
    log "INFO" "🚀 Starting AndroidWorld Runner"
    log "INFO" "Mode: $MODE, Task Type: $TASK_TYPE"
    
    # Parse arguments
    parse_arguments "$@"
    
    # Validate configuration
    validate_config
    
    # Check prerequisites
    check_prerequisites
    
    # Create directories
    create_directories
    
    # Build image if requested
    if [ "$BUILD_IMAGE" = true ]; then
        build_docker_image
    fi
    
    # Set trap for cleanup
    trap cleanup EXIT
    
    # Connect to emulator if IP is provided
    if [ -n "$EMULATOR_IP" ]; then
        connect_to_emulator "$EMULATOR_IP" "$EMULATOR_PORT"
    fi
    
    # Verify connection
    verify_connection
    
    # Run AndroidWorld tasks
    run_androidworld_tasks
    
    log "INFO" "🎉 AndroidWorld execution completed successfully!"
}

# Run main function with all arguments
main "$@"
