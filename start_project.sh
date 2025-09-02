#!/bin/bash

echo "Starting Agentics Project..."

# 检查数据库是否已运行，如果没有则启动
if ! docker ps | grep -q agentics_mysql; then
    echo "Starting database containers..."
    source backend/docker/start_databases.sh
else
    echo "Database containers already running."
fi

echo "Starting backend server..."
cd backend
python manage.py runserver &
BACKEND_PID=$!
cd ..

echo "Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "Project started successfully!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo "Admin: http://localhost:8000/admin"
echo ""
echo "Press Ctrl+C to stop all services"

# 创建停止函数
cleanup() {
    echo "Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "Services stopped. Databases are still running."
    echo "To stop databases: cd backend/docker && ./stop_databases.sh"
    exit 0
}

trap cleanup INT

wait