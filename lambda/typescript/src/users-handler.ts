/**
 * Users Lambda Handler - TypeScript Implementation
 * Author: Ali Ucer
 * Created: 2024
 * Description: REST API endpoints for user management with idempotency and retry logic
 */

import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, GetCommand, PutCommand, UpdateCommand, DeleteCommand } from '@aws-sdk/lib-dynamodb';
import { APIGatewayProxyEvent, APIGatewayProxyResult, Context } from 'aws-lambda';

// Initialize clients
const client = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(client);
const tableName = process.env.USERS_TABLE_NAME!;

interface User {
  userId: string;
  email: string;
  name?: string;
  department?: string;
  createdAt: number;
  ttl: number;
  updatedAt?: number;
}

interface Response {
  statusCode: number;
  body: string;
  headers?: Record<string, string>;
}

async function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function handler(event: APIGatewayProxyEvent, context: Context): Promise<APIGatewayProxyResult> {
  const method = event.httpMethod;
  const pathParameters = event.pathParameters || {};
  const userId = pathParameters.id;
  
  console.log('Request received', { path: event.path, method, userId });
  
  const body = event.body ? JSON.parse(event.body) : {};
  
  try {
    switch (method) {
      case 'GET':
        if (userId) {
          return await getUser(userId);
        }
        break;
      case 'POST':
        return await createUser(body);
      case 'PUT':
        if (userId) {
          return await updateUser(userId, body);
        }
        break;
      case 'DELETE':
        if (userId) {
          return await deleteUser(userId);
        }
        break;
    }
    
    return {
      statusCode: 405,
      body: JSON.stringify({ error: 'Method not allowed' })
    };
  } catch (error: any) {
    console.error('Handler error', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Internal server error' })
    };
  }
}

async function getUser(userId: string): Promise<APIGatewayProxyResult> {
  console.log('Getting user', { userId });
  
  const retries = 3;
  let backoff = 100;
  
  for (let attempt = 0; attempt < retries; attempt++) {
    try {
      const command = new GetCommand({
        TableName: tableName,
        Key: { userId }
      });
      
      const response = await docClient.send(command);
      
      if (!response.Item) {
        return {
          statusCode: 404,
          body: JSON.stringify({ error: 'User not found' })
        };
      }
      
      return {
        statusCode: 200,
        body: JSON.stringify(response.Item)
      };
    } catch (error) {
      if (attempt < retries - 1) {
        await sleep(backoff * Math.pow(2, attempt));
        console.warn('Retrying getUser', { attempt: attempt + 1 });
        continue;
      }
      throw error;
    }
  }
  
  return {
    statusCode: 500,
    body: JSON.stringify({ error: 'Failed to get user' })
  };
}

async function createUser(body: any): Promise<APIGatewayProxyResult> {
  const userId = body.userId;
  const email = body.email;
  
  if (!userId || !email) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'userId and email are required' })
    };
  }
  
  console.log('Creating user', { userId, email });
  
  try {
    // Check if user already exists (idempotency)
    const getCommand = new GetCommand({
      TableName: tableName,
      Key: { userId }
    });
    
    const existing = await docClient.send(getCommand);
    
    if (existing.Item) {
      console.log('User already exists', { userId });
      return {
        statusCode: 200,
        body: JSON.stringify({ message: 'User already exists', user: existing.Item })
      };
    }
    
    const now = Math.floor(Date.now() / 1000);
    const item: User = {
      userId,
      email,
      createdAt: now,
      ttl: now + (90 * 24 * 60 * 60) // TTL: 90 days
    };
    
    if (body.name) item.name = body.name;
    if (body.department) item.department = body.department;
    
    const command = new PutCommand({
      TableName: tableName,
      Item: item,
      ConditionExpression: 'attribute_not_exists(userId)' // Conditional write for idempotency
    });
    
    await docClient.send(command);
    
    console.log('User created successfully', { userId });
    
    return {
      statusCode: 201,
      body: JSON.stringify({ message: 'User created', user: item })
    };
  } catch (error: any) {
    if (error.name === 'ConditionalCheckFailedException') {
      console.log('User already exists (race condition)', { userId });
      const getCommand = new GetCommand({
        TableName: tableName,
        Key: { userId }
      });
      const existing = await docClient.send(getCommand);
      if (existing.Item) {
        return {
          statusCode: 200,
          body: JSON.stringify({ message: 'User already exists', user: existing.Item })
        };
      }
    }
    throw error;
  }
}

async function updateUser(userId: string, body: any): Promise<APIGatewayProxyResult> {
  console.log('Updating user', { userId });
  
  try {
    const getCommand = new GetCommand({
      TableName: tableName,
      Key: { userId }
    });
    
    const existing = await docClient.send(getCommand);
    
    if (!existing.Item) {
      return {
        statusCode: 404,
        body: JSON.stringify({ error: 'User not found' })
      };
    }
    
    const updateExpr: string[] = ['SET updatedAt = :updatedAt'];
    const exprAttr: any = { ':updatedAt': Math.floor(Date.now() / 1000) };
    
    for (const [key, value] of Object.entries(body)) {
      if (key !== 'userId') {
        updateExpr.push(`${key} = :${key}`);
        exprAttr[`:${key}`] = value;
      }
    }
    
    const command = new UpdateCommand({
      TableName: tableName,
      Key: { userId },
      UpdateExpression: updateExpr.join(', '),
      ExpressionAttributeValues: exprAttr,
      ReturnValues: 'ALL_NEW'
    });
    
    const response = await docClient.send(command);
    
    return {
      statusCode: 200,
      body: JSON.stringify(response.Attributes)
    };
  } catch (error) {
    console.error('DynamoDB update error', error);
    throw error;
  }
}

async function deleteUser(userId: string): Promise<APIGatewayProxyResult> {
  console.log('Deleting user', { userId });
  
  try {
    const command = new DeleteCommand({
      TableName: tableName,
      Key: { userId }
    });
    
    await docClient.send(command);
    
    return {
      statusCode: 200,
      body: JSON.stringify({ message: 'User deleted successfully' })
    };
  } catch (error) {
    console.error('DynamoDB delete error', error);
    throw error;
  }
}

export { handler };

