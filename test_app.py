import pytest
import json
import os
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Create a test products file
        test_products = [
            {
                "id": 1,
                "name": "Test Laptop",
                "category": "Electronics",
                "quantity": 5,
                "price": 1000.00,
                "supplier": "Test Supplier"
            },
            {
                "id": 2,
                "name": "Test Chair",
                "category": "Furniture",
                "quantity": 0,
                "price": 100.00,
                "supplier": "Test Furniture"
            }
        ]
        with open('products.json', 'w') as f:
            json.dump(test_products, f)
        yield client
        # Clean up after tests
        if os.path.exists('products.json'):
            os.remove('products.json')

# GET /products tests
def test_get_all_products_success(client):
    """Test successful retrieval of all products"""
    response = client.get('/products')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert data[0]['name'] == 'Test Laptop'
    assert data[1]['name'] == 'Test Chair'

def test_get_all_products_empty(client):
    """Test retrieval when no products exist"""
    # Empty the products file
    with open('products.json', 'w') as f:
        json.dump([], f)
    
    response = client.get('/products')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 0

# GET /products/in-stock tests
def test_get_in_stock_products_success(client):
    """Test successful retrieval of in-stock products"""
    response = client.get('/products/in-stock')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['name'] == 'Test Laptop'
    assert data[0]['quantity'] > 0

def test_get_in_stock_products_none(client):
    """Test when no products are in stock"""
    # Update all products to have zero quantity
    with open('products.json', 'r') as f:
        products = json.load(f)
    
    for product in products:
        product['quantity'] = 0
    
    with open('products.json', 'w') as f:
        json.dump(products, f)
    
    response = client.get('/products/in-stock')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 0

# GET /products/{id} tests
def test_get_product_by_id_success(client):
    """Test successful retrieval of a product by ID"""
    response = client.get('/products/1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == 1
    assert data['name'] == 'Test Laptop'

def test_get_product_by_id_not_found(client):
    """Test retrieval of a non-existent product"""
    response = client.get('/products/999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data

# POST /products tests
def test_add_product_success(client):
    """Test successful addition of a new product"""
    new_product = {
        "name": "Test Monitor",
        "category": "Electronics",
        "quantity": 15,
        "price": 200.00,
        "supplier": "Test Electronics"
    }
    
    response = client.post('/products', 
                          json=new_product,
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == 'Test Monitor'
    assert 'id' in data
    
    # Verify product was added to the file
    with open('products.json', 'r') as f:
        products = json.load(f)
    
    assert len(products) == 3
    assert any(p['name'] == 'Test Monitor' for p in products)

def test_add_product_missing_fields(client):
    """Test adding a product with missing required fields"""
    incomplete_product = {
        "name": "Incomplete Product",
        "category": "Test"
        # Missing quantity, price, and supplier
    }
    
    response = client.post('/products', 
                          json=incomplete_product,
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

# DELETE /products/{id} tests
def test_delete_product_success(client):
    """Test successful deletion of a product"""
    response = client.delete('/products/1')
    assert response.status_code == 200
    
    # Verify product was deleted
    with open('products.json', 'r') as f:
        products = json.load(f)
    
    assert len(products) == 1
    assert all(p['id'] != 1 for p in products)

def test_delete_product_not_found(client):
    """Test deletion of a non-existent product"""
    response = client.delete('/products/999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data 