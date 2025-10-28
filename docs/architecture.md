# Architecture Documentation

## System Overview

The Serverless Backend API is a cloud-native application built entirely on AWS serverless services. It provides REST API endpoints for managing users and assets, with automatic scaling, high availability, and cost-effective billing.

## Components

### API Gateway
- **Service**: AWS API Gateway (HTTP API)
- **Purpose**: Entry point for all API requests
- **Features**:
  - REST API with proper HTTP methods
  - CORS enabled
  - Request routing to appropriate Lambda functions
  - Automatic throttling and rate limiting

### Lambda Functions

#### Python Functions
- **Runtime**: Python 3.11
- **Memory**: 512 MB
- **Timeout**: 30 seconds
- **Functions**:
  - `users_handler.py`: Handles all user CRUD operations
  - `assets_handler.py`: Handles asset metadata and S3 operations

#### TypeScript Functions
- **Runtime**: Node.js 20.x
- **Memory**: 512 MB
- **Timeout**: 30 seconds
- **Functions**:
  - `users-handler.ts`: TypeScript implementation of user operations
  - `assets-handler.ts`: TypeScript implementation of asset operations

### DynamoDB

#### Users Table
- **Partition Key**: `userId` (String)
- **Attributes**:
  - `email` (String, indexed)
  - `name` (String)
  - `department` (String)
  - `createdAt` (Number, indexed)
  - `updatedAt` (Number)
  - `ttl` (Number, enables automatic expiry)
- **GSIs**:
  - `email-index`: For lookups by email
  - `createdAt-index`: For sorting by creation time
- **Billing**: On-demand (pay per request)

#### Assets Table
- **Partition Key**: `assetId` (String)
- **Attributes**:
  - `fileName` (String)
  - `contentType` (String)
  - `s3Key` (String)
  - `s3Bucket` (String)
  - `status` (String, indexed)
  - `createdAt` (Number, indexed)
  - `ttl` (Number, 30-day expiry)
- **GSIs**:
  - `status-index`: For filtering by status
  - `createdAt-index`: For time-based queries
- **Billing**: On-demand

### S3

#### Assets Bucket
- **Name**: `{stack-name}-assets`
- **Features**:
  - Private bucket (no public access)
  - Lifecycle rule: Delete objects after 30 days
  - Presigned URLs for secure upload/download
  - Prefix structure: `assets/{assetId}/{fileName}`

## Data Flow

### User Operations

```
Client → API Gateway → Lambda (Python/TS) → DynamoDB
                                      ↓
                                 Response ←
```

### Asset Operations

#### Upload Flow
```
1. Client → POST /assets → Lambda
2. Lambda creates metadata in DynamoDB
3. Lambda generates presigned S3 upload URL
4. Client uploads file directly to S3
5. Client can verify upload via GET /assets/{id}
```

#### Download Flow
```
1. Client → GET /assets/{id}/download
2. Lambda retrieves metadata from DynamoDB
3. Lambda generates presigned S3 download URL
4. Client downloads file directly from S3
```

## Security

### IAM Roles

Each Lambda function has a minimal IAM role with:
- DynamoDB read/write permissions for specific tables
- S3 read/write permissions for specific bucket
- CloudWatch Logs write permissions

### Network Security
- No VPC configuration (Lambda in default VPC)
- API Gateway handles HTTPS/TLS termination
- S3 bucket with public access blocked

### Data Security
- Sensitive data not logged
- Presigned URLs expire after 1 hour
- No data stored in Lambda code or environment variables

## Performance

### Latency Targets
- API Gateway: < 50ms
- Lambda cold start: < 1s
- Lambda warm: < 100ms
- DynamoDB: < 10ms
- Total API latency: < 1s (cold), < 200ms (warm)

### Scalability
- Lambda: Auto-scales up to 1000 concurrent executions
- DynamoDB: Auto-scales with on-demand billing
- API Gateway: Unlimited requests per second
- S3: Unlimited storage and requests

### Optimization
- Lambda function warming (via scheduled EventBridge rule)
- DynamoDB on-demand billing (no capacity planning)
- CloudFront caching for static responses

## Monitoring

### CloudWatch Metrics
- API Gateway: Request count, latency, error rate
- Lambda: Invocations, errors, duration, throttles
- DynamoDB: Consumed capacity, read/write throttles
- Alarms: Latency > 1000ms, errors > 10/min

### Logging
- Structured logs with request IDs
- Python: `structlog` for structured logging
- TypeScript: Built-in console.log with JSON
- CloudWatch Logs Insights for queries

## Cost Optimization

### DynamoDB
- On-demand billing: Pay per request
- TTL enabled: Automatic cleanup reduces storage
- GSI optimization: Only necessary indexes

### Lambda
- 512MB memory: Balance of cost and performance
- Provisioned concurrency: Not needed for this use case
- AWS Free Tier: 1M requests/month free

### S3
- Lifecycle rules: Automatic cleanup after 30 days
- No Glacier: Cost not worth complexity

### Estimated Costs (1000 requests/day)
- API Gateway: $0 (within Free Tier)
- Lambda: $0.20/month
- DynamoDB: $0.25/month (on-demand)
- S3: $0.01/month (5GB storage)
- Total: ~$0.50/month

## Disaster Recovery

### Backup Strategy
- DynamoDB: Point-in-time recovery (backup window: 35 days)
- S3: Versioning disabled (lifecycle rules handle cleanup)
- Infrastructure: Version controlled in Git

### Recovery Time
- DynamoDB PITR: < 5 minutes
- Infrastructure redeploy: ~10 minutes
- Total RTO: < 15 minutes

### Recovery Procedure
1. Identify failure point
2. Restore DynamoDB to point-in-time
3. Redeploy infrastructure with SAM
4. Run integration tests
5. Resume operations

## Development Workflow

### Local Development
1. Run `sam local start-api`
2. Test against local endpoints
3. Use SAM CLI for debugging

### Deployment
1. Run tests locally
2. Create feature branch
3. Push to GitHub
4. CI/CD runs tests
5. Manual approval for main branch
6. SAM deploys to AWS

### Rollback
1. Identify last known good commit
2. Update SAM template if needed
3. Redeploy with `sam deploy`
4. Update application tags in GitHub

## Future Enhancements

### Short Term
- [ ] Add authentication (Cognito)
- [ ] Add request validation
- [ ] Add API rate limiting per user
- [ ] Add GraphQL endpoint

### Medium Term
- [ ] Add ElasticSearch for search
- [ ] Add EventBridge for async operations
- [ ] Add SQS for message queuing
- [ ] Implement blue-green deployments

### Long Term
- [ ] Add multi-region support
- [ ] Add container-based Lambda
- [ ] Add ML-based recommendations
- [ ] Add real-time notifications (WebSocket API)

