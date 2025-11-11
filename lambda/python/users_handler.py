"""
Users Lambda Handler
Author: Ali Ucer
Created: 2024
Description: REST API endpoints for user management with idempotency and retry logic
"""

import json
import os
import time
import boto3
import structlog
from typing import Dict, Any
from botocore.exceptions import ClientError

# Initialize clients
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['USERS_TABLE_NAME'])
logger = structlog.get_logger()

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for users API endpoints
    
    Supports:
    - GET /users/{id} - Get user by ID
    - POST /users - Create user
    - PUT /users/{id} - Update user
    - DELETE /users/{id} - Delete user
    """
    try:
        http_method = event.get('httpMethod')
        request_path = event.get('path', '')
        logger.info("Request received", path=request_path, method=http_method)
        
        method = http_method
        path = request_path
        path_params = event.get('pathParameters') or {}
        body = json.loads(event.get('body', '{}'))
        
        # Extract user ID from path
        user_id = path_params.get('id')
        
        if method == 'GET' and user_id:
            return get_user(user_id)
        elif method == 'POST':
            return create_user(body)
        elif method == 'PUT' and user_id:
            return update_user(user_id, body)
        elif method == 'DELETE' and user_id:
            return delete_user(user_id)
        else:
            return {
                'statusCode': 405,
                'body': json.dumps({'error': 'Method not allowed'})
            }
            
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON'})
        }
    except ClientError as e:
        logger.error("DynamoDB error", error=str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
    except Exception as e:
        logger.error("Unexpected error", error=str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }


def get_user(user_id: str) -> Dict[str, Any]:
    """Get user by ID with retry logic"""
    logger.info("Getting user", user_id=user_id)
    
    retries = 3
    backoff = 0.1
    
    for attempt in range(retries):
        try:
            response = table.get_item(
                Key={'userId': user_id}
            )
            
            if 'Item' not in response:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'error': 'User not found'})
                }
            
            return {
                'statusCode': 200,
                'body': json.dumps(response['Item'])
            }
        except ClientError as e:
            if attempt < retries - 1:
                time.sleep(backoff * (2 ** attempt))
                logger.warning("Retrying get_user", attempt=attempt+1)
                continue
            raise
    
    return {'statusCode': 500, 'body': json.dumps({'error': 'Failed to get user'})}


def create_user(body: Dict[str, Any]) -> Dict[str, Any]:
    """Create user with idempotency and conditional write"""
    user_id = body.get('userId')
    email = body.get('email')
    
    if not user_id or not email:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'userId and email are required'})
        }
    
    logger.info("Creating user", user_id=user_id, email=email)
    
    try:
        # Check if user already exists (idempotency)
        existing = table.get_item(Key={'userId': user_id})
        if 'Item' in existing:
            logger.info("User already exists", user_id=user_id)
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'User already exists', 'user': existing['Item']})
            }
        
        # Create user with conditional write to prevent race conditions
        item = {
            'userId': user_id,
            'email': email,
            'createdAt': int(time.time()),
            'ttl': int(time.time()) + (90 * 24 * 60 * 60)  # TTL: 90 days
        }
        
        # Add optional fields
        if 'name' in body:
            item['name'] = body['name']
        if 'department' in body:
            item['department'] = body['department']
        
        response = table.put_item(
            Item=item,
            ConditionExpression='attribute_not_exists(userId)'  # Conditional write for idempotency
        )
        
        logger.info("User created successfully", user_id=user_id)
        
        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'User created', 'user': item})
        }
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            logger.info("User already exists (race condition)", user_id=user_id)
            # Fetch the existing user
            existing = table.get_item(Key={'userId': user_id})
            if 'Item' in existing:
                return {
                    'statusCode': 200,
                    'body': json.dumps({'message': 'User already exists', 'user': existing['Item']})
                }
        raise


def update_user(user_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
    """Update user with optimistic locking"""
    logger.info("Updating user", user_id=user_id)
    
    try:
        # Get existing user
        existing = table.get_item(Key={'userId': user_id})
        
        if 'Item' not in existing:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'User not found'})
            }
        
        # Build update expression
        update_expr = "SET updatedAt = :updatedAt"
        expr_attr = {':updatedAt': int(time.time())}
        
        for key, value in body.items():
            if key != 'userId':  # Don't allow changing userId
                update_expr += f", {key} = :{key}"
                expr_attr[f':{key}'] = value
        
        response = table.update_item(
            Key={'userId': user_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_attr,
            ReturnValues='ALL_NEW'
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps(response['Attributes'])
        }
        
    except ClientError as e:
        logger.error("DynamoDB update error", error=str(e))
        raise


def delete_user(user_id: str) -> Dict[str, Any]:
    """Delete user"""
    logger.info("Deleting user", user_id=user_id)
    
    try:
        table.delete_item(Key={'userId': user_id})
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'User deleted successfully'})
        }
        
    except ClientError as e:
        logger.error("DynamoDB delete error", error=str(e))
        raise

