# Contributing to Serverless Backend API

Thank you for your interest in contributing!

## Getting Started

1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/Serverless-Backend-API.git
   cd Serverless-Backend-API
   ```

3. **Set up development environment**:
   ```bash
   ./scripts/setup.sh
   ```

4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Guidelines

### Code Style

#### Python
- Use Black for formatting
- Follow PEP 8 guidelines
- Maximum line length: 100 characters
- Use type hints where possible

#### TypeScript
- Use Prettier for formatting
- Follow ESLint rules
- Use strict mode
- Prefer `const` and `let` over `var`

### Testing

Always write tests for new features:

- **Unit tests**: Test individual functions
- **Integration tests**: Test API endpoints
- **Mock external services**: Use `moto` for AWS services

Run tests:
```bash
make test
```

### Commit Messages

Use conventional commit format:
```
type(scope): description

Example:
feat(users): add user email verification
fix(assets): fix S3 presigned URL expiration
docs(readme): update installation instructions
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

## Pull Request Process

1. **Update tests**: Ensure all tests pass
2. **Update documentation**: Update README if needed
3. **Run linters**: `make lint`
4. **Create PR**: Push to your fork and create a pull request

### PR Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] No linter errors
- [ ] Commit messages follow convention
- [ ] PR description is clear

## Adding New Features

### New API Endpoint

1. Create Lambda handler:
   - Python: `lambda/python/handler_name.py`
   - TypeScript: `lambda/typescript/src/handler-name.ts`

2. Update SAM template:
   - Add Lambda function in `infrastructure/template.yaml`
   - Configure API Gateway route

3. Write tests:
   - Unit tests in `__tests__/unit/`
   - Integration tests in `__tests__/integration/`

4. Update documentation:
   - Update `docs/api-reference.md`
   - Add examples if needed

### New DynamoDB Table

1. Add table to SAM template:
   ```yaml
   NewTable:
     Type: AWS::DynamoDB::Table
     Properties:
       # ... configuration
   ```

2. Update Lambda permissions:
   - Add `DynamoDBCrudPolicy` to Lambda function

3. Update tests to mock new table

## Debugging

### Local Testing

Run locally:
```bash
make local
```

Test endpoints:
```bash
curl http://localhost:3000/users
```

### AWS Deployment Issues

Check CloudWatch Logs:
```bash
aws logs tail /aws/lambda/your-function-name --follow
```

Check CloudFormation events:
```bash
aws cloudformation describe-stack-events \
  --stack-name serverless-backend-api
```

## Questions?

Open an issue or contact maintainers.

