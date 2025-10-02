#!/bin/bash

# This script tests all available API endpoints

set -e

API_BASE="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🧪 Testing User Profile API...${NC}"
echo "=================================="

# Function to test endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local expected_status=${4:-200}
    
    echo -e "\n${YELLOW}Testing: $description${NC}"
    echo "Endpoint: $method $endpoint"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$API_BASE$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_BASE$endpoint")
    fi
    
    # Split response and status code
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ Status: $status_code${NC}"
        if [ -n "$body" ] && [ "$body" != "null" ]; then
            echo "Response:"
            echo "$body" | jq . 2>/dev/null || echo "$body"
        fi
    else
        echo -e "${RED}❌ Expected: $expected_status, Got: $status_code${NC}"
        echo "Response: $body"
    fi
}

# Check if API is running
echo "Checking if API is running..."
if ! curl -s "$API_BASE/health" > /dev/null; then
    echo -e "${RED}❌ API is not running at $API_BASE${NC}"
    echo "Please start the backend server first:"
    echo "  cd backend && python app.py"
    exit 1
fi

echo -e "${GREEN}✅ API is running${NC}"

# Test all endpoints
test_endpoint "GET" "/health" "Health Check"
test_endpoint "GET" "/api/users/1" "Get User Data (cached)"
test_endpoint "POST" "/api/users/refresh" "Force Refresh User Data"
test_endpoint "GET" "/api/users/1?bypassCache=true" "Get User Data (bypass cache)"

# Test ORM-based endpoints
echo -e "\n${YELLOW}Testing ORM-based Endpoints:${NC}"
test_endpoint "GET" "/api/users" "Get All Users"
test_endpoint "GET" "/api/users/count" "Get User Count"
test_endpoint "GET" "/api/users/stale" "Get Stale Users"
test_endpoint "GET" "/api/users/1" "Get User by ID"

# Test error cases
echo -e "\n${YELLOW}Testing Error Cases:${NC}"
test_endpoint "GET" "/api/users/999" "Invalid User ID" 404
test_endpoint "PUT" "/api/users/1" "Wrong HTTP Method" 405

# Test API documentation
echo -e "\n${YELLOW}API Documentation:${NC}"
echo "Swagger UI: $API_BASE/docs"
echo "OpenAPI Schema: $API_BASE/openapi.json"

# Performance test
echo -e "\n${YELLOW}Performance Test:${NC}"
echo "Testing response time..."
time curl -s "$API_BASE/api/users/1" > /dev/null

echo -e "\n${GREEN}🎉 All tests completed!${NC}"
echo "=================================="
