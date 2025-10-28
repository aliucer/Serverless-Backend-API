# API Reference

Base URL: `https://{api-id}.execute-api.{region}.amazonaws.com/v1`

## Authentication

Currently, the API does not require authentication. Future versions will support AWS IAM authentication or API keys.

## Users API

### Create User

Creates a new user in the system.

**Endpoint**: `POST /users`

**Request Body**:
```json
{
  "userId": "user123",
  "email": "user@example.com",
  "name": "John Doe",
  "department": "Engineering"
}
```

**Required Fields**: `userId`, `email`

**Response** (201 Created):
```json
{
  "message": "User created",
  "user": {
    "userId": "user123",
    "email": "user@example.com",
    "name": "John Doe",
    "department": "Engineering",
    "createdAt": 1704067200,
    "ttl": 1735603200
  }
}
```

**Idempotency**: Creating a user with the same `userId` multiple times will return the existing user with status 200.

### Get User

Retrieves user information by ID.

**Endpoint**: `GET /users/{userId}`

**Response** (200 OK):
```json
{
  "userId": "user123",
  "email": "user@example.com",
  "name": "John Doe",
  "department": "Engineering",
  "createdAt": 1704067200,
  "updatedAt": 1704070800,
  "ttl": 1735603200
}
```

**Response** (404 Not Found):
```json
{
  "error": "User not found"
}
```

### Update User

Updates user information. Only provided fields will be updated.

**Endpoint**: `PUT /users/{userId}`

**Request Body**:
```json
{
  "name": "Jane Doe",
  "department": "Marketing"
}
```

**Response** (200 OK):
```json
{
  "userId": "user123",
  "email": "user@example.com",
  "name": "Jane Doe",
  "department": "Marketing",
  "createdAt": 1704067200,
  "updatedAt": 1704070800
}
```

**Notes**:
- `userId` cannot be changed
- Only provided fields are updated
- Automatically updates `updatedAt` timestamp

### Delete User

Deletes a user from the system.

**Endpoint**: `DELETE /users/{userId}`

**Response** (200 OK):
```json
{
  "message": "User deleted successfully"
}
```

## Assets API

### Create Asset

Creates asset metadata and returns presigned URL for uploading the file.

**Endpoint**: `POST /assets`

**Request Body**:
```json
{
  "assetId": "asset123",
  "fileName": "document.pdf",
  "contentType": "application/pdf"
}
```

**Required Fields**: `assetId`, `fileName`

**Response** (201 Created):
```json
{
  "message": "Asset metadata created",
  "asset": {
    "assetId": "asset123",
    "fileName": "document.pdf",
    "contentType": "application/pdf",
    "s3Key": "assets/asset123/document.pdf",
    "s3Bucket": "serverless-backend-api-assets",
    "status": "pending",
    "createdAt": 1704067200,
    "ttl": 1706678400
  },
  "uploadUrl": "https://s3.amazonaws.com/bucket/assets/asset123/document.pdf?X-Amz-Algorithm=..."
}
```

**Idempotency**: Creating an asset with the same `assetId` will return the existing asset metadata.

**Next Steps**: Use the `uploadUrl` to upload the file using a PUT request.

### Get Asset Metadata

Retrieves asset metadata by ID.

**Endpoint**: `GET /assets/{assetId}`

**Response** (200 OK):
```json
{
  "assetId": "asset123",
  "fileName": "document.pdf",
  "contentType": "application/pdf",
  "s3Key": "assets/asset123/document.pdf",
  "s3Bucket": "serverless-backend-api-assets",
  "status": "pending",
  "createdAt": 1704067200,
  "ttl": 1706678400
}
```

### Get Download URL

Returns a presigned URL for downloading the asset.

**Endpoint**: `GET /assets/{assetId}/download`

**Response** (200 OK):
```json
{
  "downloadUrl": "https://s3.amazonaws.com/bucket/assets/asset123/document.pdf?X-Amz-Algorithm=...",
  "fileName": "document.pdf",
  "contentType": "application/pdf"
}
```

**Notes**:
- Presigned URLs expire after 1 hour
- Use the download URL directly to fetch the file

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

- `200 OK` - Success
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request format or missing required fields
- `404 Not Found` - Resource not found
- `405 Method Not Allowed` - HTTP method not supported for this endpoint
- `500 Internal Server Error` - Server error

## Rate Limits

Currently, the API has no rate limits. Future versions may implement:
- 1000 requests/hour per user
- 10,000 requests/day per user
- Rate limit headers will be included in responses

## Pagination

Currently, list endpoints are not implemented. When added:
- Use `limit` query parameter for page size
- Use `nextToken` for pagination

## Examples

### Python

```python
import requests

# Create user
response = requests.post(
    'https://api-id.execute-api.us-east-1.amazonaws.com/v1/users',
    json={
        'userId': 'user123',
        'email': 'user@example.com',
        'name': 'John Doe'
    }
)
print(response.json())

# Get user
response = requests.get(
    'https://api-id.execute-api.us-east-1.amazonaws.com/v1/users/user123'
)
print(response.json())
```

### JavaScript/TypeScript

```typescript
async function createUser() {
  const response = await fetch(
    'https://api-id.execute-api.us-east-1.amazonaws.com/v1/users',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId: 'user123',
        email: 'user@example.com',
        name: 'John Doe'
      })
    }
  );
  
  const data = await response.json();
  console.log(data);
}

async function getUser(userId: string) {
  const response = await fetch(
    `https://api-id.execute-api.us-east-1.amazonaws.com/v1/users/${userId}`
  );
  
  const user = await response.json();
  console.log(user);
}
```

### cURL

```bash
# Create user
curl -X POST https://api-id.execute-api.us-east-1.amazonaws.com/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user123",
    "email": "user@example.com",
    "name": "John Doe"
  }'

# Get user
curl https://api-id.execute-api.us-east-1.amazonaws.com/v1/users/user123

# Update user
curl -X PUT https://api-id.execute-api.us-east-1.amazonaws.com/v1/users/user123 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe"
  }'

# Delete user
curl -X DELETE https://api-id.execute-api.us-east-1.amazonaws.com/v1/users/user123
```

## Webhooks & Events

Coming soon: EventBridge integration for async operations and webhooks.

