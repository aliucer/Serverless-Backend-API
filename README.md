# Serverless Backend API

A production-ready serverless REST API built with AWS Lambda, API Gateway, DynamoDB, and S3. Implemented in both Python and TypeScript to demonstrate serverless architecture patterns.

**Author**: Ali Ucer  
**Created**: 2024

## Overview

This project demonstrates building a scalable serverless backend on AWS, implementing modern practices including:
- REST API endpoints with idempotency
- DynamoDB with proper schema design and GSIs
- S3 integration for file storage
- CI/CD pipeline with GitHub Actions
- CloudWatch monitoring and alarms
- Retry logic with exponential backoff
- Unit and integration testing

## Technologies

- **Python 3.11** and **TypeScript** - Lambda runtime
- **AWS Lambda** - Serverless compute
- **API Gateway** - REST API management
- **DynamoDB** - NoSQL database with GSIs and TTL
- **S3** - Object storage with presigned URLs
- **CloudWatch** - Logging and monitoring
- **AWS SAM** - Infrastructure as code
- **GitHub Actions** - CI/CD pipeline

## Architecture

```
API Gateway
    ↓
Lambda Functions (Python/TypeScript)
    ↓
    ├─→ DynamoDB (Users & Assets tables)
    └─→ S3 (File storage)
```

## Features

### Users API
- `GET /users/{id}` - Retrieve user by ID
- `POST /users` - Create new user (idempotent)
- `PUT /users/{id}` - Update user information
- `DELETE /users/{id}` - Delete user

### Assets API
- `POST /assets` - Create asset and get presigned upload URL
- `GET /assets/{id}` - Retrieve asset metadata
- `GET /assets/{id}/download` - Get presigned download URL

Both APIs implement retry logic with exponential backoff for reliability.

## Project Structure

```
serverless-backend-api/
├── lambda/
│   ├── python/              # Python Lambda functions
│   └── typescript/          # TypeScript Lambda functions
├── infrastructure/
│   └── template.yaml        # AWS SAM template
├── __tests__/
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── .github/
│   └── workflows/           # CI/CD pipeline
└── docs/                   # Documentation
```

## Getting Started

### Prerequisites

- AWS Account
- AWS SAM CLI
- Python 3.11+
- Node.js 20+
- Docker (for local testing)

### Installation

```bash
git clone https://github.com/aliucer/Serverless-Backend-API.git
cd Serverless-Backend-API
./scripts/setup.sh
```

### Local Development

```bash
make local
```

API available at `http://localhost:3000`

### Deployment

```bash
aws configure
make deploy
```

## Implementation Details

### DynamoDB Schema

**Users Table**
- Partition Key: `userId` (String)
- GSIs: `email-index`, `createdAt-index`
- TTL: 90 days

**Assets Table**
- Partition Key: `assetId` (String)
- GSIs: `status-index`, `createdAt-index`
- TTL: 30 days

### Features

**Idempotency**  
Conditional writes prevent duplicate operations using `attribute_not_exists()`.

**Retry Logic**  
Exponential backoff: 3 attempts with delays (0.1s → 0.2s → 0.4s).

**Monitoring**  
CloudWatch alarms for latency (>1s) and errors (>10/min).

**CI/CD**  
GitHub Actions automatically tests and deploys on push to main branch.

## API Usage

### Create User
```bash
curl -X POST https://api-id.execute-api.us-east-1.amazonaws.com/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user123",
    "email": "user@example.com",
    "name": "John Doe"
  }'
```

### Get User
```bash
curl https://api-id.execute-api.us-east-1.amazonaws.com/v1/users/user123
```

### Create Asset
```bash
curl -X POST https://api-id.execute-api.us-east-1.amazonaws.com/v1/assets \
  -H "Content-Type: application/json" \
  -d '{
    "assetId": "asset123",
    "fileName": "document.pdf",
    "contentType": "application/pdf"
  }'
```

## Testing

```bash
# Run all tests
make test

# Python tests
pytest __tests__/unit/test_users_handler.py -v

# Integration tests
pytest __tests__/integration/ -v
```

## Development

```bash
# Format code
make format

# Lint code
make lint

# Build project
make build
```

## Performance

- DynamoDB on-demand billing for cost optimization
- Lambda memory: 512MB
- S3 lifecycle rules for automatic cleanup (30 days)
- TTL on tables for data lifecycle management

Estimated cost: less than $1/month for moderate usage.

## Security

- IAM roles with least privilege access
- S3 bucket with public access blocked
- Presigned URLs for secure file access
- No sensitive data in logs

## Future Enhancements

- AWS Cognito authentication
- GraphQL endpoint
- Real-time notifications
- Multi-region support

## Author

Ali Ucer
