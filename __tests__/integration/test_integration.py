"""
Integration tests for the serverless backend API.

These tests require AWS credentials and resources to be deployed.
Set TEST_ENV variable to the deployed stack name.
"""

import pytest
import boto3
import requests
import json
import os
import time
from typing import Dict, Any

# Configuration
API_ENDPOINT = os.environ.get('API_ENDPOINT', 'http://localhost:3000')
USERS_ENDPOINT = f'{API_ENDPOINT}/users'
ASSETS_ENDPOINT = f'{API_ENDPOINT}/assets'


@pytest.fixture
def test_user_data():
    """Fixture for test user data"""
    return {
        'userId': f'test-user-{int(time.time())}',
        'email': f'test-{int(time.time())}@example.com',
        'name': 'Integration Test User'
    }


@pytest.fixture
def test_asset_data():
    """Fixture for test asset data"""
    return {
        'assetId': f'test-asset-{int(time.time())}',
        'fileName': 'test-file.txt',
        'contentType': 'text/plain'
    }


class TestUsersAPI:
    """Integration tests for Users API"""
    
    def test_create_user(self, test_user_data: Dict[str, Any]):
        """Test creating a user"""
        response = requests.post(
            USERS_ENDPOINT,
            json=test_user_data
        )
        
        assert response.status_code in [201, 200]
        data = response.json()
        assert 'user' in data or response.status_code == 200
    
    def test_create_user_idempotency(self, test_user_data: Dict[str, Any]):
        """Test idempotent user creation"""
        # First creation
        response1 = requests.post(
            USERS_ENDPOINT,
            json=test_user_data
        )
        assert response1.status_code in [201, 200]
        
        # Second creation (should be idempotent)
        response2 = requests.post(
            USERS_ENDPOINT,
            json=test_user_data
        )
        assert response2.status_code == 200
        assert 'already exists' in response2.json()['message'].lower()
    
    def test_get_user(self, test_user_data: Dict[str, Any]):
        """Test retrieving a user"""
        # Create user first
        create_response = requests.post(
            USERS_ENDPOINT,
            json=test_user_data
        )
        assert create_response.status_code in [201, 200]
        
        # Get user
        get_response = requests.get(f'{USERS_ENDPOINT}/{test_user_data["userId"]}')
        assert get_response.status_code == 200
        
        data = get_response.json()
        assert data['userId'] == test_user_data['userId']
        assert data['email'] == test_user_data['email']
    
    def test_get_nonexistent_user(self):
        """Test retrieving a non-existent user"""
        response = requests.get(f'{USERS_ENDPOINT}/nonexistent-user-id')
        assert response.status_code == 404
        assert 'not found' in response.json()['error'].lower()
    
    def test_update_user(self, test_user_data: Dict[str, Any]):
        """Test updating a user"""
        # Create user first
        create_response = requests.post(
            USERS_ENDPOINT,
            json=test_user_data
        )
        assert create_response.status_code in [201, 200]
        
        # Update user
        updated_data = {'name': 'Updated Name'}
        update_response = requests.put(
            f'{USERS_ENDPOINT}/{test_user_data["userId"]}',
            json=updated_data
        )
        assert update_response.status_code == 200
        
        data = update_response.json()
        assert data['name'] == 'Updated Name'
    
    def test_delete_user(self, test_user_data: Dict[str, Any]):
        """Test deleting a user"""
        # Create user first
        create_response = requests.post(
            USERS_ENDPOINT,
            json=test_user_data
        )
        assert create_response.status_code in [201, 200]
        
        # Delete user
        delete_response = requests.delete(
            f'{USERS_ENDPOINT}/{test_user_data["userId"]}'
        )
        assert delete_response.status_code == 200
        
        # Verify user is deleted
        get_response = requests.get(f'{USERS_ENDPOINT}/{test_user_data["userId"]}')
        assert get_response.status_code == 404
    
    def test_create_user_missing_fields(self):
        """Test creating user with missing required fields"""
        incomplete_data = {'userId': 'test-user'}
        
        response = requests.post(
            USERS_ENDPOINT,
            json=incomplete_data
        )
        
        assert response.status_code == 400
        assert 'required' in response.json()['error'].lower()


class TestAssetsAPI:
    """Integration tests for Assets API"""
    
    def test_create_asset(self, test_asset_data: Dict[str, Any]):
        """Test creating an asset"""
        response = requests.post(
            ASSETS_ENDPOINT,
            json=test_asset_data
        )
        
        assert response.status_code in [201, 200]
        data = response.json()
        assert 'asset' in data
        if response.status_code == 201:
            assert 'uploadUrl' in data
    
    def test_get_asset(self, test_asset_data: Dict[str, Any]):
        """Test retrieving asset metadata"""
        # Create asset first
        create_response = requests.post(
            ASSETS_ENDPOINT,
            json=test_asset_data
        )
        assert create_response.status_code in [201, 200]
        
        # Get asset
        get_response = requests.get(f'{ASSETS_ENDPOINT}/{test_asset_data["assetId"]}')
        assert get_response.status_code == 200
        
        data = get_response.json()
        assert data['assetId'] == test_asset_data['assetId']
        assert data['fileName'] == test_asset_data['fileName']
    
    def test_get_download_url(self, test_asset_data: Dict[str, Any]):
        """Test getting presigned download URL"""
        # Create asset first
        create_response = requests.post(
            ASSETS_ENDPOINT,
            json=test_asset_data
        )
        assert create_response.status_code in [201, 200]
        
        # Get download URL
        download_response = requests.get(
            f'{ASSETS_ENDPOINT}/{test_asset_data["assetId"]}/download'
        )
        assert download_response.status_code == 200
        
        data = download_response.json()
        assert 'downloadUrl' in data
        assert 'fileName' in data
    
    def test_get_nonexistent_asset(self):
        """Test retrieving a non-existent asset"""
        response = requests.get(f'{ASSETS_ENDPOINT}/nonexistent-asset-id')
        assert response.status_code == 404
        assert 'not found' in response.json()['error'].lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

