#!/bin/bash
set -e

echo "Setting up Serverless Backend API..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed"
    exit 1
fi

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "Installing AWS SAM CLI..."
    pip install aws-sam-cli
fi

# Install Python dependencies
echo "Installing Python dependencies..."
cd lambda/python
pip install -r requirements.txt

# Install TypeScript dependencies
echo "Installing TypeScript dependencies..."
cd ../typescript
npm install

# Build TypeScript
echo "Building TypeScript..."
npm run build

cd ../..

echo "Setup complete!"
echo ""
echo "To run tests: make test"
echo "To deploy: make deploy"
echo "To run locally: make local"

