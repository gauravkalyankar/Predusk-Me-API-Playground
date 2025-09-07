import pytest
import json
from base64 import b64encode
from backend.app import app, USERNAME, PASSWORD
from backend.database import init_db
from backend.seed import seed_data

@pytest.fixture
def client():
    """
    Pytest fixture to set up the test client.
    This runs before each test function.
    """
    # Use an in-memory SQLite database for testing
    app.config['DATABASE'] = 'file:memory:?cache=shared'
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            # Initialize and seed the database for each test
            init_db()
            seed_data()
        yield client

def get_auth_headers():
    """Helper function to create Basic Auth headers."""
    creds = f"{USERNAME}:{PASSWORD}"
    encoded_creds = b64encode(creds.encode('utf-8')).decode('utf-8')
    return {
        'Authorization': f'Basic {encoded_creds}'
    }

# --- Test Cases ---

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {"status": "healthy"}

def test_get_profile(client):
    """Test fetching the main profile."""
    response = client.get('/profile')
    assert response.status_code == 200
    data = response.json
    assert data['name'] == 'Gaurav Kalyankar'
    assert 'projects' in data
    assert 'skills' in data

def test_get_projects_paginated(client):
    """Test the paginated projects endpoint."""
    # Request the first page with 1 project per page
    response = client.get('/projects?page=1&per_page=1')
    assert response.status_code == 200
    data = response.json
    assert data['page'] == 1
    assert data['total_pages'] == 2 # Based on 2 seeded projects
    assert len(data['items']) == 1

def test_update_profile_unauthorized(client):
    """Test that updating the profile fails without authentication."""
    response = client.put('/profile', json={'name': 'New Name'})
    assert response.status_code == 401 # Unauthorized

def test_update_profile_authorized(client):
    """Test that updating the profile succeeds with correct authentication."""
    headers = get_auth_headers()
    response = client.put('/profile', json={'name': 'Gaurav K.'}, headers=headers)
    assert response.status_code == 200
    assert response.json['message'] == "Profile name updated to Gaurav K."

    # Verify the change was made
    profile_response = client.get('/profile')
    assert profile_response.json['name'] == 'Gaurav K.'