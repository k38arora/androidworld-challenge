#!/bin/bash

# Test Setup Script for AndroidWorld with Genymotion
# This script tests the basic setup and functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧪 Testing AndroidWorld Setup${NC}"
echo "This script will test the basic setup and functionality"

# Test 1: Check if scripts are executable
test_script_permissions() {
    echo -e "${YELLOW}📋 Test 1: Checking script permissions...${NC}"
    
    local scripts=("run.sh" "infra/deploy-cloud.sh" "infra/start-local-emulator.sh")
    local all_executable=true
    
    for script in "${scripts[@]}"; do
        if [ -x "$script" ]; then
            echo -e "  ✅ $script is executable"
        else
            echo -e "  ❌ $script is not executable"
            all_executable=false
        fi
    done
    
    if [ "$all_executable" = true ]; then
        echo -e "${GREEN}✅ All scripts are executable${NC}"
        return 0
    else
        echo -e "${RED}❌ Some scripts are not executable${NC}"
        return 1
    fi
}

# Test 2: Check if Dockerfile exists
test_dockerfile() {
    echo -e "${YELLOW}📋 Test 2: Checking Dockerfile...${NC}"
    
    if [ -f "Dockerfile" ]; then
        echo -e "  ✅ Dockerfile exists"
        return 0
    else
        echo -e "  ❌ Dockerfile not found"
        return 1
    fi
}

# Test 3: Check if requirements.txt exists
test_requirements() {
    echo -e "${YELLOW}📋 Test 3: Checking requirements.txt...${NC}"
    
    if [ -f "requirements.txt" ]; then
        echo -e "  ✅ requirements.txt exists"
        return 0
    else
        echo -e "  ❌ requirements.txt not found"
        return 1
    fi
}

# Test 4: Check if README exists
test_readme() {
    echo -e "${YELLOW}📋 Test 4: Checking README.md...${NC}"
    
    if [ -f "README.md" ]; then
        echo -e "  ✅ README.md exists"
        return 0
    else
        echo -e "  ❌ README.md not found"
        return 1
    fi
}

# Test 5: Test run.sh help
test_run_help() {
    echo -e "${YELLOW}📋 Test 5: Testing run.sh help...${NC}"
    
    if ./run.sh --help &>/dev/null; then
        echo -e "  ✅ run.sh help works"
        return 0
    else
        echo -e "  ❌ run.sh help failed"
        return 1
    fi
}

# Test 6: Test local emulator script help
test_local_help() {
    echo -e "${YELLOW}📋 Test 6: Testing local emulator script help...${NC}"
    
    if ./infra/start-local-emulator.sh --help &>/dev/null; then
        echo -e "  ✅ start-local-emulator.sh help works"
        return 0
    else
        echo -e "  ❌ start-local-emulator.sh help failed"
        return 1
    fi
}

# Test 7: Check directory structure
test_directory_structure() {
    echo -e "${YELLOW}📋 Test 7: Checking directory structure...${NC}"
    
    local required_dirs=("infra" "logs" "outputs")
    local all_dirs_exist=true
    
    for dir in "${required_dirs[@]}"; do
        if [ -d "$dir" ]; then
            echo -e "  ✅ Directory $dir exists"
        else
            echo -e "  ❌ Directory $dir missing"
            all_dirs_exist=false
        fi
    done
    
    if [ "$all_dirs_exist" = true ]; then
        echo -e "${GREEN}✅ All required directories exist${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Some directories are missing (will be created at runtime)${NC}"
        return 0
    fi
}

# Test 8: Test Docker build (optional)
test_docker_build() {
    echo -e "${YELLOW}📋 Test 8: Testing Docker build (optional)...${NC}"
    
    if command -v docker &> /dev/null; then
        if docker info &>/dev/null; then
            echo -e "  🔍 Docker is available, testing build..."
            if docker build -t androidworld:test . &>/dev/null; then
                echo -e "  ✅ Docker build successful"
                # Clean up test image
                docker rmi androidworld:test &>/dev/null || true
                return 0
            else
                echo -e "  ❌ Docker build failed"
                return 1
            fi
        else
            echo -e "  ⚠️  Docker daemon not running"
            return 0
        fi
    else
        echo -e "  ⚠️  Docker not installed"
        return 0
    fi
}

# Main test function
main() {
    echo -e "${BLUE}🔍 Starting setup tests...${NC}"
    echo ""
    
    local tests_passed=0
    local tests_total=8
    
    # Run all tests
    test_script_permissions && tests_passed=$((tests_passed + 1))
    test_dockerfile && tests_passed=$((tests_passed + 1))
    test_requirements && tests_passed=$((tests_passed + 1))
    test_readme && tests_passed=$((tests_passed + 1))
    test_run_help && tests_passed=$((tests_passed + 1))
    test_local_help && tests_passed=$((tests_passed + 1))
    test_directory_structure && tests_passed=$((tests_passed + 1))
    test_docker_build && tests_passed=$((tests_passed + 1))
    
    echo ""
    echo -e "${BLUE}📊 Test Results:${NC}"
    echo -e "  Tests passed: ${GREEN}$tests_passed${NC}/$tests_total"
    
    if [ $tests_passed -eq $tests_total ]; then
        echo -e "${GREEN}🎉 All tests passed! Setup is ready.${NC}"
        echo ""
        echo -e "${YELLOW}Next steps:${NC}"
        echo "1. For local testing: ./infra/start-local-emulator.sh"
        echo "2. For cloud deployment: ./infra/deploy-cloud.sh"
        echo "3. Run AndroidWorld: ./run.sh --local --test"
        return 0
    else
        echo -e "${YELLOW}⚠️  Some tests failed. Please check the issues above.${NC}"
        return 1
    fi
}

# Run main function
main "$@"
