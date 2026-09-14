#!/usr/bin/env bash
# startup.sh — run this on any VPS / Docker host / Cloud Shell
# Builds the React frontend then starts the FastAPI server (serves both)
set -e

echo "==> Building React frontend..."
cd frontend
npm install --prefer-offline
npm run build
cd ..

echo "==> Starting FastAPI server (serves API + frontend)..."
PORT=${PORT:-8000}
uvicorn api.main:app --host 0.0.0.0 --port "$PORT" --workers 1
