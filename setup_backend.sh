#!/bin/bash

echo "Setting up Agentics Backend..."

# 启动数据库容器
source backend/docker/start_databases.sh

cd backend

# echo "Creating virtual environment..."
# uv venv --python 3.12
# source .venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Creating .env file..."
cp .env.example .env

echo "Waiting for databases to be fully ready..."
sleep 10

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Creating superuser..."
python manage.py createsuperuser --noinput --username admin --email admin@example.com || true

echo "Backend setup complete!"
echo "To start services:"
echo "  Backend only: cd backend && python manage.py runserver"
echo "  Full project: ./start_project.sh"
echo "To stop databases: cd backend/docker && ./stop_databases.sh"