#!/bin/bash

# Local Genymotion Emulator Setup Script
# This script helps set up and start Genymotion emulators locally

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🏠 Local Genymotion Emulator Setup${NC}"
echo "This script will help you set up Genymotion emulators locally"

# Check if Genymotion is installed
check_genymotion() {
    echo -e "${YELLOW}📋 Checking Genymotion installation...${NC}"
    
    if command -v genymotion &> /dev/null; then
        echo -e "${GREEN}✅ Genymotion found in PATH${NC}"
        return 0
    elif [ -f "/Applications/Genymotion.app/Contents/MacOS/genymotion" ]; then
        echo -e "${GREEN}✅ Genymotion found in Applications (macOS)${NC}"
        export PATH="/Applications/Genymotion.app/Contents/MacOS:$PATH"
        return 0
    elif [ -f "/opt/genymotion/genymotion" ]; then
        echo -e "${GREEN}✅ Genymotion found in /opt/genymotion${NC}"
        export PATH="/opt/genymotion:$PATH"
        return 0
    else
        echo -e "${RED}❌ Genymotion not found${NC}"
        return 1
    fi
}

# Check ADB installation
check_adb() {
    echo -e "${YELLOW}📱 Checking ADB installation...${NC}"
    
    if command -v adb &> /dev/null; then
        echo -e "${GREEN}✅ ADB found${NC}"
        return 0
    else
        echo -e "${RED}❌ ADB not found${NC}"
        echo -e "${YELLOW}Please install Android SDK or Android Studio to get ADB${NC}"
        return 1
    fi
}

# Start ADB server
start_adb_server() {
    echo -e "${YELLOW}🚀 Starting ADB server...${NC}"
    
    adb start-server
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ ADB server started${NC}"
    else
        echo -e "${RED}❌ Failed to start ADB server${NC}"
        exit 1
    fi
}

# List available devices
list_devices() {
    echo -e "${YELLOW}📱 Checking for connected devices...${NC}"
    
    adb devices
}

# Start Genymotion emulator
start_emulator() {
    echo -e "${YELLOW}🎮 Starting Genymotion emulator...${NC}"
    
    # Check if Genymotion is running
    if pgrep -f "genymotion" > /dev/null; then
        echo -e "${GREEN}✅ Genymotion is already running${NC}"
    else
        echo -e "${BLUE}🚀 Launching Genymotion...${NC}"
        
        # Try to start Genymotion
        if genymotion &> /dev/null & then
            echo -e "${GREEN}✅ Genymotion started successfully${NC}"
            echo -e "${YELLOW}⏳ Waiting for emulator to boot...${NC}"
            sleep 30
        else
            echo -e "${RED}❌ Failed to start Genymotion${NC}"
            echo -e "${YELLOW}Please start Genymotion manually and try again${NC}"
            exit 1
        fi
    fi
}

# Wait for emulator to be ready
wait_for_emulator() {
    echo -e "${YELLOW}⏳ Waiting for emulator to be ready...${NC}"
    
    local max_attempts=60
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if adb devices | grep -q "emulator\|device"; then
            echo -e "${GREEN}✅ Emulator is ready!${NC}"
            return 0
        fi
        
        echo -n "."
        sleep 5
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ Emulator failed to start within timeout${NC}"
    return 1
}

# Install test app (optional)
install_test_app() {
    echo -e "${YELLOW}📱 Installing test app...${NC}"
    
    # Create a simple test app if none exists
    if [ ! -f "test-app.apk" ]; then
        echo -e "${BLUE}Creating test APK...${NC}"
        # This is a placeholder - in real scenarios you'd have actual APKs
        echo "Test APK placeholder" > test-app.apk
    fi
    
    # Try to install the app
    if adb install test-app.apk &> /dev/null; then
        echo -e "${GREEN}✅ Test app installed${NC}"
    else
        echo -e "${YELLOW}⚠️  Could not install test app (this is normal for placeholder)${NC}"
    fi
}

# Main setup function
main() {
    echo -e "${BLUE}🔍 Starting local emulator setup...${NC}"
    
    # Check prerequisites
    if ! check_genymotion; then
        echo -e "${RED}❌ Please install Genymotion first${NC}"
        echo -e "${YELLOW}Download from: https://www.genymotion.com/download/${NC}"
        exit 1
    fi
    
    if ! check_adb; then
        echo -e "${RED}❌ Please install ADB first${NC}"
        echo -e "${YELLOW}Install Android Studio or Android SDK${NC}"
        exit 1
    fi
    
    # Start services
    start_adb_server
    start_emulator
    
    # Wait for emulator
    if wait_for_emulator; then
        list_devices
        install_test_app
        
        echo -e "${GREEN}🎉 Local emulator setup completed successfully!${NC}"
        echo ""
        echo -e "${YELLOW}Next steps:${NC}"
        echo "1. Your emulator should now be visible in Genymotion"
        echo "2. Run 'adb devices' to see connected devices"
        echo "3. Use './run.sh --local' to run AndroidWorld"
    else
        echo -e "${RED}❌ Setup failed. Please check Genymotion and try again${NC}"
        exit 1
    fi
}

# Show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  --check-only   Only check prerequisites without starting emulator"
    echo ""
    echo "This script sets up Genymotion emulators locally for AndroidWorld testing."
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    --check-only)
        check_genymotion
        check_adb
        echo -e "${GREEN}✅ Prerequisites check completed${NC}"
        exit 0
        ;;
    "")
        main
        ;;
    *)
        echo -e "${RED}❌ Unknown option: $1${NC}"
        show_help
        exit 1
        ;;
esac
