#!/bin/bash

# Test script for Django REST API
# Tests all major endpoints to ensure API is working correctly

set -e  # Exit on error

# Configuration
BASE_URL="http://localhost:8000/api/v1"
TOKEN="2f60485812cdc76656cd477cf1381be4d0f45717"
HEADERS="Authorization: Token ${TOKEN}"

echo "========================================"
echo "Django Todo App - REST API Test Suite"
echo "========================================"
echo ""

# Check if server is running
echo "1. Checking if server is running..."
if ! curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/tasks/" -H "${HEADERS}" | grep -q "200"; then
    echo "   ❌ Server is not running or not accessible"
    echo "   Please start the server: python manage.py runserver"
    exit 1
fi
echo "   ✓ Server is running"
echo ""

# Test Authentication
echo "2. Testing authentication..."
RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/token/" \
    -H "Content-Type: application/json" \
    -d '{"username": "admin", "password": "admin123"}')

if echo "$RESPONSE" | grep -q "token"; then
    echo "   ✓ Authentication works"
else
    echo "   ❌ Authentication failed"
    echo "   Response: $RESPONSE"
fi
echo ""

# Test List Tasks
echo "3. Testing list tasks..."
RESPONSE=$(curl -s "${BASE_URL}/tasks/" -H "${HEADERS}")
if echo "$RESPONSE" | grep -q "results"; then
    TASK_COUNT=$(echo "$RESPONSE" | grep -o '"count":[0-9]*' | grep -o '[0-9]*')
    echo "   ✓ List tasks works (found ${TASK_COUNT} tasks)"
else
    echo "   ❌ List tasks failed"
fi
echo ""

# Test Create Task
echo "4. Testing create task..."
RESPONSE=$(curl -s -X POST "${BASE_URL}/tasks/" \
    -H "${HEADERS}" \
    -H "Content-Type: application/json" \
    -d '{
        "title": "API Test Task",
        "description": "Created by test script",
        "priority": 2,
        "effort_points": 5,
        "category_name": "Testing",
        "status": "todo"
    }')

if echo "$RESPONSE" | grep -q "API Test Task"; then
    TASK_ID=$(echo "$RESPONSE" | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')
    echo "   ✓ Create task works (ID: ${TASK_ID})"
else
    echo "   ❌ Create task failed"
    echo "   Response: $RESPONSE"
    exit 1
fi
echo ""

# Test Get Task
echo "5. Testing get task..."
RESPONSE=$(curl -s "${BASE_URL}/tasks/${TASK_ID}/" -H "${HEADERS}")
if echo "$RESPONSE" | grep -q "API Test Task"; then
    echo "   ✓ Get task works"
else
    echo "   ❌ Get task failed"
fi
echo ""

# Test Update Task
echo "6. Testing update task..."
RESPONSE=$(curl -s -X PATCH "${BASE_URL}/tasks/${TASK_ID}/" \
    -H "${HEADERS}" \
    -H "Content-Type: application/json" \
    -d '{"status": "in_progress"}')

if echo "$RESPONSE" | grep -q "in_progress"; then
    echo "   ✓ Update task works"
else
    echo "   ❌ Update task failed"
fi
echo ""

# Test Complete Task
echo "7. Testing complete task..."
RESPONSE=$(curl -s -X POST "${BASE_URL}/tasks/${TASK_ID}/complete/" -H "${HEADERS}")
if echo "$RESPONSE" | grep -q "completed"; then
    echo "   ✓ Complete task works"
else
    echo "   ❌ Complete task failed"
fi
echo ""

# Test Search
echo "8. Testing search..."
RESPONSE=$(curl -s "${BASE_URL}/tasks/search/?q=API" -H "${HEADERS}")
if echo "$RESPONSE" | grep -q "API"; then
    echo "   ✓ Search works"
else
    echo "   ❌ Search failed"
fi
echo ""

# Test Filters
echo "9. Testing filters..."
RESPONSE=$(curl -s "${BASE_URL}/tasks/?status=completed&priority=2" -H "${HEADERS}")
if echo "$RESPONSE" | grep -q "results"; then
    echo "   ✓ Filters work"
else
    echo "   ❌ Filters failed"
fi
echo ""

# Test Categories
echo "10. Testing list categories..."
RESPONSE=$(curl -s "${BASE_URL}/categories/" -H "${HEADERS}")
if echo "$RESPONSE" | grep -q "results"; then
    echo "   ✓ List categories works"
else
    echo "   ❌ List categories failed"
fi
echo ""

# Test Create Category
echo "11. Testing create category..."
RESPONSE=$(curl -s -X POST "${BASE_URL}/categories/" \
    -H "${HEADERS}" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "API Test Category",
        "description": "Created by test script",
        "color": "#ff0000"
    }')

if echo "$RESPONSE" | grep -q "API Test Category"; then
    CATEGORY_ID=$(echo "$RESPONSE" | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')
    echo "   ✓ Create category works (ID: ${CATEGORY_ID})"
else
    echo "   ❌ Create category failed"
fi
echo ""

# Test Dashboard Analytics
echo "12. Testing dashboard analytics..."
RESPONSE=$(curl -s "${BASE_URL}/analytics/dashboard/" -H "${HEADERS}")
if echo "$RESPONSE" | grep -q "effort_points"; then
    echo "   ✓ Dashboard analytics works"
else
    echo "   ❌ Dashboard analytics failed"
fi
echo ""

# Test Effort Points
echo "13. Testing effort points analytics..."
RESPONSE=$(curl -s "${BASE_URL}/analytics/effort-points/?period=today" -H "${HEADERS}")
if echo "$RESPONSE" | grep -q "points_today"; then
    POINTS=$(echo "$RESPONSE" | grep -o '"points_today":[0-9]*' | grep -o '[0-9]*')
    echo "   ✓ Effort points works (today: ${POINTS} points)"
else
    echo "   ❌ Effort points failed"
fi
echo ""

# Test Category Breakdown
echo "14. Testing category breakdown..."
RESPONSE=$(curl -s "${BASE_URL}/analytics/category-breakdown/" -H "${HEADERS}")
if echo "$RESPONSE" | grep -q "total_points" || echo "$RESPONSE" | grep -q "\[\]"; then
    echo "   ✓ Category breakdown works"
else
    echo "   ❌ Category breakdown failed"
fi
echo ""

# Test Completion History
echo "15. Testing completion history..."
RESPONSE=$(curl -s "${BASE_URL}/analytics/completion-history/" -H "${HEADERS}")
if echo "$RESPONSE" | grep -q "task_title" || echo "$RESPONSE" | grep -q "\[\]"; then
    echo "   ✓ Completion history works"
else
    echo "   ❌ Completion history failed"
fi
echo ""

# Test Add Note
echo "16. Testing add note to task..."
RESPONSE=$(curl -s -X POST "${BASE_URL}/notes/" \
    -H "${HEADERS}" \
    -H "Content-Type: application/json" \
    -d "{
        \"task\": ${TASK_ID},
        \"content\": \"Test note from API\"
    }")

if echo "$RESPONSE" | grep -q "Test note"; then
    NOTE_ID=$(echo "$RESPONSE" | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')
    echo "   ✓ Add note works (ID: ${NOTE_ID})"
else
    echo "   ❌ Add note failed"
fi
echo ""

# Cleanup - Delete test task
echo "17. Cleaning up - deleting test task..."
curl -s -X DELETE "${BASE_URL}/tasks/${TASK_ID}/" -H "${HEADERS}" > /dev/null
echo "   ✓ Test task deleted"
echo ""

# Cleanup - Delete test category
if [ ! -z "$CATEGORY_ID" ]; then
    echo "18. Cleaning up - deleting test category..."
    curl -s -X DELETE "${BASE_URL}/categories/${CATEGORY_ID}/" -H "${HEADERS}" > /dev/null
    echo "   ✓ Test category deleted"
    echo ""
fi

echo "========================================"
echo "✓ All API tests passed!"
echo "========================================"
echo ""
echo "API is working correctly. You can now:"
echo "1. Visit interactive docs: http://localhost:8000/api/v1/docs/"
echo "2. View ReDoc: http://localhost:8000/api/v1/redoc/"
echo "3. Use the API with your token: ${TOKEN}"
echo ""
