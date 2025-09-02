#!/bin/bash

echo "Setting up Agentics Frontend..."

cd frontend

echo "Installing dependencies..."
npm install

echo "Creating .env file..."
cp .env.example .env

echo "Frontend setup complete!"
echo "To start the frontend server, run:"
echo "cd frontend && npm start"