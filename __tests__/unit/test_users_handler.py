import json
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../lambda/python')))

from unittest.mock import patch, MagicMock, call
from users_handler import handler, get_user, create_user, update_user, delete_user
from botocore.exceptions import ClientError


@patch('users_handler.table')
@patch('users_handler.logger')
def test_get_user_success(mock_logger, mock_table):
    """Test successful user retrieval"""
    user_id = 'user123'
    mock_item = {
        'userId': user_id,
        'email': 'test@example.com',
        'name': 'Test User'
    }
    
    mock_table.get_item.return_value = {'Item': mock_item}
    
    result = get_user(user_id)
    
    assert result['statusCode'] == 200
    data = json.loads(result['body'])
    assert data['userId'] == user_id
    mock_table.get_item.assert_called_once_with(Key={'userId': user_id})


@patch('users_handler.table')
def test_get_user_not_found(mock_table):
    """Test user not found scenario"""
    user_id = 'nonexistent'
    
    mock_table.get_item.return_value = {}
    
    result = get_user(user_id)
    
    assert result['statusCode'] == 404
    data = json.loads(result['body'])
    assert data['error'] == 'User not found'


@patch('users_handler.table')
@patch('users_handler.time')
def test_create_user_success(mock_time, mock_table):
    """Test successful user creation"""
    mock_time.time.return_value = 1000
    
    body = {
        'userId': 'user123',
        'email': 'test@example.com',
        'name': 'Test User'
    }
    
    # Mock that user doesn't exist
    mock_table.get_item.return_value = {}
    
    result = create_user(body)
    
    assert result['statusCode'] == 201
    data = json.loads(result['body'])
    assert data['message'] == 'User created'
    assert 'user' in data
    
    # Verify put_item was called with correct parameters
    call_args = mock_table.put_item.call_args
    assert call_args[1]['ConditionExpression'] == 'attribute_not_exists(userId)'


@patch('users_handler.table')
def test_create_user_idempotency(mock_table):
    """Test idempotent user creation"""
    existing_user = {
        'userId': 'user123',
        'email': 'test@example.com'
    }
    
    # Mock that user already exists
    mock_table.get_item.return_value = {'Item': existing_user}
    
    body = {
        'userId': 'user123',
        'email': 'test@example.com'
    }
    
    result = create_user(body)
    
    assert result['statusCode'] == 200
    data = json.loads(result['body'])
    assert data['message'] == 'User already exists'


@patch('users_handler.table')
def test_create_user_missing_required_fields(mock_table):
    """Test user creation with missing required fields"""
    body = {'userId': 'user123'}  # Missing email
    
    result = create_user(body)
    
    assert result['statusCode'] == 400
    data = json.loads(result['body'])
    assert 'required' in data['error']
    mock_table.put_item.assert_not_called()


@patch('users_handler.table')
def test_update_user_success(mock_table):
    """Test successful user update"""
    user_id = 'user123'
    body = {'name': 'Updated Name'}
    
    # Mock existing user
    mock_table.get_item.return_value = {
        'Item': {
            'userId': user_id,
            'email': 'test@example.com'
        }
    }
    
    mock_table.update_item.return_value = {
        'Attributes': {
            'userId': user_id,
            'email': 'test@example.com',
            'name': 'Updated Name'
        }
    }
    
    result = update_user(user_id, body)
    
    assert result['statusCode'] == 200
    data = json.loads(result['body'])
    assert data['name'] == 'Updated Name'


@patch('users_handler.table')
def test_update_user_not_found(mock_table):
    """Test update of non-existent user"""
    user_id = 'nonexistent'
    body = {'name': 'Updated Name'}
    
    mock_table.get_item.return_value = {}
    
    result = update_user(user_id, body)
    
    assert result['statusCode'] == 404
    data = json.loads(result['body'])
    assert data['error'] == 'User not found'


@patch('users_handler.table')
def test_delete_user_success(mock_table):
    """Test successful user deletion"""
    user_id = 'user123'
    
    result = delete_user(user_id)
    
    assert result['statusCode'] == 200
    data = json.loads(result['body'])
    assert data['message'] == 'User deleted successfully'
    mock_table.delete_item.assert_called_once_with(Key={'userId': user_id})


@patch('users_handler.logger')
def test_handler_invalid_json(mock_logger):
    """Test handler with invalid JSON"""
    event = {
        'httpMethod': 'POST',
        'body': 'invalid json'
    }
    
    result = handler(event, None)
    
    assert result['statusCode'] == 400


def test_handler_get_user():
    """Test handler with GET request"""
    event = {
        'httpMethod': 'GET',
        'path': '/users/user123',
        'pathParameters': {'id': 'user123'},
        'body': '{}'
    }
    
    with patch('users_handler.get_user') as mock_get:
        mock_get.return_value = {'statusCode': 200, 'body': '{}'}
        result = handler(event, None)
        mock_get.assert_called_once_with('user123')


def test_handler_post_user():
    """Test handler with POST request"""
    event = {
        'httpMethod': 'POST',
        'path': '/users',
        'body': json.dumps({'userId': 'user123', 'email': 'test@example.com'})
    }
    
    with patch('users_handler.create_user') as mock_create:
        mock_create.return_value = {'statusCode': 201, 'body': '{}'}
        result = handler(event, None)
        mock_create.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

