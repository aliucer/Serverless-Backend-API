import json
import os
import boto3
import structlog
from typing import Dict, Any
from botocore.exceptions import ClientError

# Initialize clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['ASSETS_TABLE_NAME'])
logger = structlog.get_logger()

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for assets API endpoints
    
    Supports:
    - POST /assets - Upload asset
    - GET /assets/{id} - Get asset metadata
    - GET /assets/{id}/download - Get signed URL for download
    """
    try:
        logger.info("Asset request received", path=event.get('path'), method=event.get('httpMethod'))
        
        method = event.get('httpMethod')
        path = event.get('path', '')
        path_params = event.get('pathParameters') or {}
        body = json.loads(event.get('body', '{}'))
        
        asset_id = path_params.get('id')
        action = path_params.get('action', '')
        
        if method == 'POST':
            return upload_asset(body)
        elif method == 'GET' and asset_id:
            if action == 'download':
                return get_download_url(asset_id)
            else:
                return get_asset(asset_id)
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
        logger.error("AWS service error", error=str(e))
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


def upload_asset(body: Dict[str, Any]) -> Dict[str, Any]:
    """Create asset metadata in DynamoDB and return upload URL"""
    asset_id = body.get('assetId')
    file_name = body.get('fileName')
    content_type = body.get('contentType', 'application/octet-stream')
    
    if not asset_id or not file_name:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'assetId and fileName are required'})
        }
    
    logger.info("Creating asset metadata", asset_id=asset_id, file_name=file_name)
    
    try:
        import time
        import uuid
        
        bucket_name = os.environ['ASSETS_BUCKET_NAME']
        s3_key = f"assets/{asset_id}/{file_name}"
        
        # Check if asset already exists (idempotency)
        existing = table.get_item(Key={'assetId': asset_id})
        if 'Item' in existing:
            logger.info("Asset already exists", asset_id=asset_id)
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Asset already exists', 'asset': existing['Item']})
            }
        
        # Store metadata in DynamoDB
        item = {
            'assetId': asset_id,
            'fileName': file_name,
            'contentType': content_type,
            's3Key': s3_key,
            's3Bucket': bucket_name,
            'status': 'pending',
            'createdAt': int(time.time()),
            'ttl': int(time.time()) + (30 * 24 * 60 * 60)  # TTL: 30 days
        }
        
        response = table.put_item(
            Item=item,
            ConditionExpression='attribute_not_exists(assetId)'
        )
        
        # Generate presigned URL for upload
        upload_url = s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': s3_key,
                'ContentType': content_type
            },
            ExpiresIn=3600  # 1 hour
        )
        
        return {
            'statusCode': 201,
            'body': json.dumps({
                'message': 'Asset metadata created',
                'asset': item,
                'uploadUrl': upload_url
            })
        }
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            existing = table.get_item(Key={'assetId': asset_id})
            if 'Item' in existing:
                return {
                    'statusCode': 200,
                    'body': json.dumps({'message': 'Asset already exists', 'asset': existing['Item']})
                }
        raise


def get_asset(asset_id: str) -> Dict[str, Any]:
    """Get asset metadata"""
    logger.info("Getting asset", asset_id=asset_id)
    
    try:
        response = table.get_item(Key={'assetId': asset_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Asset not found'})
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps(response['Item'])
        }
        
    except ClientError as e:
        logger.error("DynamoDB error", error=str(e))
        raise


def get_download_url(asset_id: str) -> Dict[str, Any]:
    """Get presigned URL for downloading asset"""
    logger.info("Getting download URL", asset_id=asset_id)
    
    try:
        response = table.get_item(Key={'assetId': asset_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Asset not found'})
            }
        
        item = response['Item']
        download_url = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': item['s3Bucket'],
                'Key': item['s3Key']
            },
            ExpiresIn=3600  # 1 hour
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'downloadUrl': download_url,
                'fileName': item['fileName'],
                'contentType': item.get('contentType')
            })
        }
        
    except ClientError as e:
        logger.error("S3/DynamoDB error", error=str(e))
        raise

