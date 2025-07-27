"""
Basic tests for the application
"""

import json


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'version' in data


def test_dashboard_api(client):
    """Test dashboard API endpoint"""
    response = client.get('/api/v1/dashboard')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'data' in data


def test_arbitrage_api(client):
    """Test arbitrage API endpoint"""
    response = client.get('/api/v1/arbitrage')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'data' in data
    assert 'opportunities' in data['data']


def test_exchanges_api(client):
    """Test exchanges API endpoint"""
    response = client.get('/api/v1/exchanges')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'data' in data


def test_tokens_api(client):
    """Test tokens API endpoint"""
    response = client.get('/api/v1/tokens')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'data' in data


def test_networks_api(client):
    """Test networks API endpoint"""
    response = client.get('/api/v1/networks')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'data' in data


def test_react_spa_route(client):
    """Test React SPA is served"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Arbitrage Platform' in response.data


def test_invalid_api_endpoint(client):
    """Test invalid API endpoint returns 404"""
    response = client.get('/api/v1/nonexistent')
    assert response.status_code == 404