# Quick Start Guide

Get up and running with the Serverless Backend API in 5 minutes.

## Prerequisites

Install these tools:
- AWS CLI: https://aws.amazon.com/cli/
- SAM CLI: `pip install aws-sam-cli`
- Python 3.11+
- Node.js 20+
- Docker (for local testing)

## Step 1: Clone and Setup

```bash
git clone https://github.com/aliucer/Serverless-Backend-API.git
cd Serverless-Backend-API

# Run setup script
./scripts/setup.sh
```

## Step 2: Configure AWS

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region: us-east-1
# Enter output format: json
```

## Step 3: Run Locally (Optional)

Test the API locally:

```bash
make local
```

In another terminal:
```bash
# Test user creation
curl -X POST http://localhost:3000/users \
  -H "Content-Type: application/json" \
  -d '{"userId":"test123","email":"test@example.com","name":"Test User"}'

# Test user retrieval
curl http://localhost:3000/users/test123
```

## Step 4: Deploy to AWS

```bash
sam build --template-file infrastructure/template.yaml
sam deploy --guided
```

Follow the prompts:
- Stack name: `serverless-backend-api`
- AWS Region: `us-east-1`
- Confirm changes: `Y`
- Allow SAM CLI IAM role creation: `Y`
- Disable rollback: `N`

## Step 5: Test Your API

Get the API endpoint from the output:
```bash
aws cloudformation describe-stacks \
  --stack-name serverless-backend-api \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue'
```

Test the API:
```bash
export API_URL="<your-api-endpoint>"

# Create a user
curl -X POST $API_URL/users \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "demo-user-1",
    "email": "demo@example.com",
    "name": "Demo User",
    "department": "Engineering"
  }'

# Get the user
curl $API_URL/users/demo-user-1

# Update the user
curl -X PUT $API_URL/users/demo-user-1 \
  -H "Content-Type: application/json" \
  -d '{"department": "Product"}'

# Delete the user
curl -X DELETE $API_URL/users/demo-user-1
```

## Common Commands

```bash
# Run tests
make test

# Run locally
make local

# Deploy
make deploy

# View logs
sam logs --stack-name serverless-backend-api --name PythonUsersGetFunction --tail

# Clean up
sam delete --stack-name serverless-backend-api
```

## Troubleshooting

### Issue: "Stack already exists"
```bash
# Update existing stack
sam deploy --no-confirm-changeset
```

### Issue: "Cannot find module"
```bash
# Rebuild
make build
sam build
```

### Issue: "Access denied"
```bash
# Check AWS credentials
aws sts get-caller-identity

# Update credentials
aws configure
```

### Issue: "Resource limit exceeded"
- Some AWS accounts have service limits
- Request limit increase from AWS Support

## Next Steps

1. Read the [README.md](README.md) for detailed documentation
2. Check [docs/architecture.md](docs/architecture.md) for system design
3. See [docs/api-reference.md](docs/api-reference.md) for API details
4. Review [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

## Support

- **Issues**: https://github.com/aliucer/Serverless-Backend-API/issues
- **Documentation**: See `/docs` directory
- **Examples**: Check `/__tests__/integration/` for API usage examples

Happy coding! 🚀

