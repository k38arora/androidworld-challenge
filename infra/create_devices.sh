#!/bin/bash

# Create Devices Script for AndroidWorld Challenge
# This script sets up Genymotion Cloud devices for evaluation

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Setting up Genymotion Cloud Devices for AndroidWorld Challenge${NC}"

# Load environment variables if .env exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Check if we have Genymotion credentials
if [[ -z "$GENYMOTION_USERNAME" || -z "$GENYMOTION_PASSWORD" ]]; then
    echo -e "${RED}❌ Missing Genymotion credentials${NC}"
    echo "Please set GENYMOTION_USERNAME and GENYMOTION_PASSWORD in your .env file"
    exit 1
fi

echo -e "${YELLOW}📱 Genymotion Cloud Mode${NC}"
echo "Creating cloud Android emulator using Genymotion Cloud..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3 first.${NC}"
    exit 1
fi

# Install required Python packages
echo -e "${YELLOW}📦 Installing required packages...${NC}"
pip3 install requests --quiet

# Run Genymotion Cloud setup
echo -e "${YELLOW}🔧 Setting up Genymotion Cloud device...${NC}"
python3 infra/genymotion_cloud_working.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Genymotion Cloud setup complete${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Note the ADB connection details from above"
    echo "2. Connect using: adb connect <host>:<port>"
    echo "3. Run: ./agents/evaluate.sh --episodes 50"
else
    echo -e "${RED}❌ Genymotion Cloud setup failed${NC}"
    echo "Please check your credentials and try again"
    exit 1
fi

echo -e "${GREEN}🎯 Device setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Ensure emulator is running"
echo "2. Run: ./agents/evaluate.sh --episodes 50"
echo "3. Check results in results/ directory"
echo "4. View report.md for evaluation summary"
