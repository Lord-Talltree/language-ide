#!/bin/bash

# L-ide Startup Script
# Starts backend and frontend in separate terminal tabs

echo "🚀 Starting L-ide..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Kill any existing processes on ports 8000 and 3000
echo "Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

sleep 1

# Start backend
echo -e "${BLUE}Starting Backend...${NC}"
cd /Users/rubenkai/Antigravity/language-ide/prototype/backend

# Check if venv exists, activate it
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start backend in background
uvicorn main:app --reload --host 0.0.0.0 --port 8000 > /tmp/lide-backend.log 2>&1 &
BACKEND_PID=$!

echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo "  Logs: tail -f /tmp/lide-backend.log"
echo "  API: http://localhost:8000/docs"
echo ""

# Wait for backend to start
sleep 3

# Start frontend
echo -e "${BLUE}Starting Frontend...${NC}"
cd /Users/rubenkai/Antigravity/language-ide/prototype/frontend

# Start frontend in background
npm run dev > /tmp/lide-frontend.log 2>&1 &
FRONTEND_PID=$!

echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
echo "  Logs: tail -f /tmp/lide-frontend.log"
echo ""

# Wait for frontend to start
sleep 5

echo ""
echo "======================================"
echo -e "${GREEN}✅ L-ide is running!${NC}"
echo "======================================"
echo ""
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000/docs"
echo ""
echo "View logs:"
echo "  Backend:  tail -f /tmp/lide-backend.log"
echo "  Frontend: tail -f /tmp/lide-frontend.log"
echo ""
echo "Stop services:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Or save PIDs to file for later:"
echo "$BACKEND_PID" > /tmp/lide-backend.pid
echo "$FRONTEND_PID" > /tmp/lide-frontend.pid
echo ""
