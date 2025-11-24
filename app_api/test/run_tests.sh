#!/bin/bash
# Quick test runner script

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Knowledge Management API Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if API is running
API_URL=${API_BASE_URL:-"http://localhost:5001"}
echo -e "${YELLOW}Checking API availability at ${API_URL}...${NC}"

if curl -s -f "${API_URL}/api/health" > /dev/null; then
    echo -e "${GREEN}✓ API is accessible${NC}"
    echo ""
else
    echo -e "\033[0;31m✗ API is not accessible at ${API_URL}${NC}"
    echo "Please ensure the API server is running:"
    echo "  cd app_api && python api.py"
    exit 1
fi

# Check if test PDF exists
if [ ! -f "$(dirname "$0")/居住证办理.pdf" ]; then
    echo -e "\033[0;31m✗ Test PDF not found: 居住证办理.pdf${NC}"
    echo "Please place the test PDF in the test directory"
    exit 1
fi

echo -e "${GREEN}✓ Test PDF found${NC}"
echo ""

# Run tests
echo -e "${BLUE}Running tests...${NC}"
echo ""

cd "$(dirname "$0")"
python3 test_api.py

exit $?
