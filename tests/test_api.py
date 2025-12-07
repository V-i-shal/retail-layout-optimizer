"""Tests for API endpoints."""
import pytest
from app.dashboard.server import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get('/health')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'


def test_api_health_endpoint(client):
    """Test API health endpoint."""
    response = client.get('/api/health')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['status'] == 'healthy'


def test_get_sections(client):
    """Test GET /api/sections endpoint."""
    response = client.get('/api/sections')
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'success' in data
    assert 'count' in data
    assert 'data' in data
    
    if data['success'] and data['count'] > 0:
        # Check first section has required fields
        section = data['data'][0]
        assert 'section_id' in section
        assert 'name' in section
        assert 'x' in section
        assert 'y' in section


def test_get_graph(client):
    """Test GET /api/graph endpoint."""
    response = client.get('/api/graph')
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'success' in data
    assert 'data' in data
    
    if data['success']:
        assert 'nodes' in data['data']
        assert 'edges' in data['data']
        assert isinstance(data['data']['nodes'], list)
        assert isinstance(data['data']['edges'], list)


def test_get_recommendations(client):
    """Test GET /api/recommendations endpoint."""
    response = client.get('/api/recommendations')
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'success' in data
    assert 'count' in data
    assert 'data' in data
    
    if data['success'] and data['count'] > 0:
        # Check first recommendation has required fields
        rec = data['data'][0]
        assert 'product_id' in rec
        assert 'recommended_section_id' in rec
        assert 'score' in rec


def test_get_recommendations_with_limit(client):
    """Test GET /api/recommendations with limit parameter."""
    response = client.get('/api/recommendations?limit=5')
    
    assert response.status_code == 200
    data = response.get_json()
    
    if data['success']:
        assert data['count'] <= 5


def test_get_products(client):
    """Test GET /api/products endpoint."""
    response = client.get('/api/products')
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'success' in data
    assert 'count' in data
    assert 'data' in data


def test_get_communities(client):
    """Test GET /api/communities endpoint."""
    response = client.get('/api/communities')
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'success' in data
    assert 'data' in data
    
    if data['success']:
        assert 'by_community' in data


def test_get_stats(client):
    """Test GET /api/stats endpoint."""
    response = client.get('/api/stats')
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert 'success' in data
    assert 'data' in data
    
    if data['success']:
        stats = data['data']
        assert 'sections' in stats
        assert 'products' in stats
        assert 'graph_edges' in stats
        assert isinstance(stats['sections'], int)


def test_index_page(client):
    """Test dashboard index page."""
    response = client.get('/')
    
    assert response.status_code == 200
    assert b'Retail Layout Optimizer' in response.data


def test_invalid_endpoint(client):
    """Test invalid endpoint returns 404."""
    response = client.get('/api/invalid')
    
    assert response.status_code == 404


if __name__ == '__main__':
    pytest.main([__file__, '-v'])