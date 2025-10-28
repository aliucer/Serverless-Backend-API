import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, GetCommand, PutCommand } from '@aws-sdk/lib-dynamodb';
import { S3Client, GetObjectCommand, PutObjectCommand } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';
import { APIGatewayProxyEvent, APIGatewayProxyResult, Context } from 'aws-lambda';

// Initialize clients
const dynamoClient = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(dynamoClient);
const s3Client = new S3Client({});

const tableName = process.env.ASSETS_TABLE_NAME!;
const bucketName = process.env.ASSETS_BUCKET_NAME!;

interface Asset {
  assetId: string;
  fileName: string;
  contentType: string;
  s3Key: string;
  s3Bucket: string;
  status: string;
  createdAt: number;
  ttl: number;
}

async function handler(event: APIGatewayProxyEvent, context: Context): Promise<APIGatewayProxyResult> {
  console.log('Asset request received', { path: event.path, method: event.httpMethod });
  
  const method = event.httpMethod;
  const pathParameters = event.pathParameters || {};
  const body = event.body ? JSON.parse(event.body) : {};
  
  const assetId = pathParameters.id;
  const action = pathParameters.action || '';
  
  try {
    switch (method) {
      case 'POST':
        return await uploadAsset(body);
      case 'GET':
        if (assetId) {
          if (action === 'download') {
            return await getDownloadUrl(assetId);
          } else {
            return await getAsset(assetId);
          }
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

async function uploadAsset(body: any): Promise<APIGatewayProxyResult> {
  const assetId = body.assetId;
  const fileName = body.fileName;
  const contentType = body.contentType || 'application/octet-stream';
  
  if (!assetId || !fileName) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'assetId and fileName are required' })
    };
  }
  
  console.log('Creating asset metadata', { assetId, fileName });
  
  try {
    const s3Key = `assets/${assetId}/${fileName}`;
    
    // Check if asset already exists (idempotency)
    const getCommand = new GetCommand({
      TableName: tableName,
      Key: { assetId }
    });
    
    const existing = await docClient.send(getCommand);
    
    if (existing.Item) {
      console.log('Asset already exists', { assetId });
      return {
        statusCode: 200,
        body: JSON.stringify({ message: 'Asset already exists', asset: existing.Item })
      };
    }
    
    const now = Math.floor(Date.now() / 1000);
    const item: Asset = {
      assetId,
      fileName,
      contentType,
      s3Key,
      s3Bucket: bucketName,
      status: 'pending',
      createdAt: now,
      ttl: now + (30 * 24 * 60 * 60) // TTL: 30 days
    };
    
    const putCommand = new PutCommand({
      TableName: tableName,
      Item: item,
      ConditionExpression: 'attribute_not_exists(assetId)'
    });
    
    await docClient.send(putCommand);
    
    // Generate presigned URL for upload
    const putObjectCommand = new PutObjectCommand({
      Bucket: bucketName,
      Key: s3Key,
      ContentType: contentType
    });
    
    const uploadUrl = await getSignedUrl(s3Client, putObjectCommand, { expiresIn: 3600 });
    
    return {
      statusCode: 201,
      body: JSON.stringify({
        message: 'Asset metadata created',
        asset: item,
        uploadUrl
      })
    };
  } catch (error: any) {
    if (error.name === 'ConditionalCheckFailedException') {
      const getCommand = new GetCommand({
        TableName: tableName,
        Key: { assetId }
      });
      const existing = await docClient.send(getCommand);
      if (existing.Item) {
        return {
          statusCode: 200,
          body: JSON.stringify({ message: 'Asset already exists', asset: existing.Item })
        };
      }
    }
    throw error;
  }
}

async function getAsset(assetId: string): Promise<APIGatewayProxyResult> {
  console.log('Getting asset', { assetId });
  
  try {
    const command = new GetCommand({
      TableName: tableName,
      Key: { assetId }
    });
    
    const response = await docClient.send(command);
    
    if (!response.Item) {
      return {
        statusCode: 404,
        body: JSON.stringify({ error: 'Asset not found' })
      };
    }
    
    return {
      statusCode: 200,
      body: JSON.stringify(response.Item)
    };
  } catch (error) {
    console.error('DynamoDB error', error);
    throw error;
  }
}

async function getDownloadUrl(assetId: string): Promise<APIGatewayProxyResult> {
  console.log('Getting download URL', { assetId });
  
  try {
    const getCommand = new GetCommand({
      TableName: tableName,
      Key: { assetId }
    });
    
    const response = await docClient.send(getCommand);
    
    if (!response.Item) {
      return {
        statusCode: 404,
        body: JSON.stringify({ error: 'Asset not found' })
      };
    }
    
    const item = response.Item as Asset;
    
    const getObjectCommand = new GetObjectCommand({
      Bucket: item.s3Bucket,
      Key: item.s3Key
    });
    
    const downloadUrl = await getSignedUrl(s3Client, getObjectCommand, { expiresIn: 3600 });
    
    return {
      statusCode: 200,
      body: JSON.stringify({
        downloadUrl,
        fileName: item.fileName,
        contentType: item.contentType
      })
    };
  } catch (error) {
    console.error('S3/DynamoDB error', error);
    throw error;
  }
}

export { handler };

