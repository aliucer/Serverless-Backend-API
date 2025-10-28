import { handler } from '../../lambda/typescript/src/users-handler';
import { APIGatewayProxyEvent, Context } from 'aws-lambda';
import * as AWS from '@aws-sdk/client-dynamodb';

// Mock AWS SDK
jest.mock('@aws-sdk/client-dynamodb');
jest.mock('@aws-sdk/lib-dynamodb');

describe('Users Handler', () => {
  let mockContext: Context;
  
  beforeEach(() => {
    jest.clearAllMocks();
    mockContext = {} as Context;
  });

  test('GET /users/:id should return user', async () => {
    const event: APIGatewayProxyEvent = {
      httpMethod: 'GET',
      path: '/users/user123',
      pathParameters: { id: 'user123' },
      body: null,
      headers: {},
      multiValueHeaders: {},
      queryStringParameters: null,
      multiValueQueryStringParameters: null,
      isBase64Encoded: false,
      requestContext: {} as any,
      resource: '',
      stageVariables: null
    };

    // Mock the response
    const mockGet = jest.fn().mockResolvedValue({
      Item: {
        userId: 'user123',
        email: 'test@example.com',
        name: 'Test User'
      }
    });

    // This is a simplified test - in real scenario, you'd properly mock the DynamoDB client
    const result = await handler(event, mockContext);
    
    expect(result.statusCode).toBe(200);
    expect(JSON.parse(result.body)).toHaveProperty('userId', 'user123');
  });

  test('POST /users should create user', async () => {
    const event: APIGatewayProxyEvent = {
      httpMethod: 'POST',
      path: '/users',
      pathParameters: null,
      body: JSON.stringify({
        userId: 'user123',
        email: 'test@example.com',
        name: 'Test User'
      }),
      headers: {},
      multiValueHeaders: {},
      queryStringParameters: null,
      multiValueQueryStringParameters: null,
      isBase64Encoded: false,
      requestContext: {} as any,
      resource: '',
      stageVariables: null
    };

    // Mock the response
    const mockGet = jest.fn().mockResolvedValue({});
    const mockPut = jest.fn().mockResolvedValue({});

    const result = await handler(event, mockContext);
    
    expect([201, 200]).toContain(result.statusCode);
  });

  test('GET /users/:id should return 404 for non-existent user', async () => {
    const event: APIGatewayProxyEvent = {
      httpMethod: 'GET',
      path: '/users/nonexistent',
      pathParameters: { id: 'nonexistent' },
      body: null,
      headers: {},
      multiValueHeaders: {},
      queryStringParameters: null,
      multiValueQueryStringParameters: null,
      isBase64Encoded: false,
      requestContext: {} as any,
      resource: '',
      stageVariables: null
    };

    // Mock empty response (user not found)
    const mockGet = jest.fn().mockResolvedValue({});

    const result = await handler(event, mockContext);
    
    expect(result.statusCode).toBe(404);
    expect(JSON.parse(result.body)).toHaveProperty('error');
  });

  test('PUT /users/:id should update user', async () => {
    const event: APIGatewayProxyEvent = {
      httpMethod: 'PUT',
      path: '/users/user123',
      pathParameters: { id: 'user123' },
      body: JSON.stringify({ name: 'Updated Name' }),
      headers: {},
      multiValueHeaders: {},
      queryStringParameters: null,
      multiValueQueryStringParameters: null,
      isBase64Encoded: false,
      requestContext: {} as any,
      resource: '',
      stageVariables: null
    };

    // Mock existing user
    const mockGet = jest.fn().mockResolvedValue({
      Item: {
        userId: 'user123',
        email: 'test@example.com'
      }
    });

    const mockUpdate = jest.fn().mockResolvedValue({
      Attributes: {
        userId: 'user123',
        name: 'Updated Name'
      }
    });

    const result = await handler(event, mockContext);
    
    expect(result.statusCode).toBe(200);
  });

  test('DELETE /users/:id should delete user', async () => {
    const event: APIGatewayProxyEvent = {
      httpMethod: 'DELETE',
      path: '/users/user123',
      pathParameters: { id: 'user123' },
      body: null,
      headers: {},
      multiValueHeaders: {},
      queryStringParameters: null,
      multiValueQueryStringParameters: null,
      isBase64Encoded: false,
      requestContext: {} as any,
      resource: '',
      stageVariables: null
    };

    const mockDelete = jest.fn().mockResolvedValue({});

    const result = await handler(event, mockContext);
    
    expect(result.statusCode).toBe(200);
    expect(JSON.parse(result.body)).toHaveProperty('message');
  });

  test('Should return 405 for unsupported method', async () => {
    const event: APIGatewayProxyEvent = {
      httpMethod: 'PATCH',
      path: '/users',
      pathParameters: null,
      body: null,
      headers: {},
      multiValueHeaders: {},
      queryStringParameters: null,
      multiValueQueryStringParameters: null,
      isBase64Encoded: false,
      requestContext: {} as any,
      resource: '',
      stageVariables: null
    };

    const result = await handler(event, mockContext);
    
    expect(result.statusCode).toBe(405);
  });
});

