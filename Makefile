.PHONY: help install build test deploy clean local

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install all dependencies
	@echo "Installing Python dependencies..."
	cd lambda/python && pip install -r requirements.txt
	@echo "Installing TypeScript dependencies..."
	cd lambda/typescript && npm install

build: ## Build the project
	@echo "Building TypeScript..."
	cd lambda/typescript && npm run build

test: ## Run tests
	@echo "Running Python tests..."
	python -m pytest __tests__/unit -v
	@echo "Running TypeScript tests..."
	cd lambda/typescript && npm test

deploy: ## Deploy to AWS
	sam build --template-file infrastructure/template.yaml
	sam deploy

local: ## Run API locally
	sam local start-api

clean: ## Clean build artifacts
	rm -rf lambda/python/*.pyc
	rm -rf lambda/python/__pycache__
	rm -rf lambda/typescript/node_modules
	rm -rf lambda/typescript/dist
	rm -rf *.zip
	rm -rf .aws-sam

format: ## Format code
	@echo "Formatting Python code..."
	black lambda/python/*.py
	@echo "Formatting TypeScript code..."
	cd lambda/typescript && npm run format || true

lint: ## Lint code
	@echo "Linting Python code..."
	flake8 lambda/python/ || true
	@echo "Linting TypeScript code..."
	cd lambda/typescript && npm run lint || true

