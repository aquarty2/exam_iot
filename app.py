from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import json
import os

app = Flask(__name__)
api = Api(app)

DATA_FILE = 'products.json'

def load_products():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_products(products):
    with open(DATA_FILE, 'w') as f:
        json.dump(products, f, indent=4)

if not os.path.exists(DATA_FILE):
    initial_products = [
        {
            "id": 1,
            "name": "Laptop",
            "category": "Electronics",
            "quantity": 10,
            "price": 1200.00,
            "supplier": "TechCorp"
        },
        {
            "id": 2,
            "name": "Desk Chair",
            "category": "Furniture",
            "quantity": 0,
            "price": 150.00,
            "supplier": "FurnitureCo"
        },
        {
            "id": 3,
            "name": "Notebook",
            "category": "Office Supplies",
            "quantity": 100,
            "price": 4.50,
            "supplier": "OfficeWorld"
        }
    ]
    save_products(initial_products)

class ProductList(Resource):
    def get(self):
        products = load_products()
        return jsonify(products)
    
    def post(self):
        products = load_products()
        new_product = request.get_json()
        
        # Validate required fields
        required_fields = ["name", "category", "quantity", "price", "supplier"]
        for field in required_fields:
            if field not in new_product:
                return {"error": f"Missing required field: {field}"}, 400
        
        # Validate data types
        if not isinstance(new_product["quantity"], int):
            return {"error": "Quantity must be an integer"}, 400
        
        try:
            new_product["price"] = float(new_product["price"])
        except (ValueError, TypeError):
            return {"error": "Price must be a number"}, 400
        
        # Generate new ID
        new_id = 1
        if products:
            new_id = max(product["id"] for product in products) + 1
        
        new_product["id"] = new_id
        products.append(new_product)
        save_products(products)
        
        return new_product, 201

class ProductInStock(Resource):
    def get(self):
        products = load_products()
        in_stock = [product for product in products if product["quantity"] > 0]
        return jsonify(in_stock)

class Product(Resource):
    def get(self, product_id):
        products = load_products()
        product = next((p for p in products if p["id"] == product_id), None)
        
        if product:
            return jsonify(product)
        return {"error": "Product not found"}, 404
    
    def delete(self, product_id):
        products = load_products()
        initial_length = len(products)
        products = [p for p in products if p["id"] != product_id]
        
        if len(products) < initial_length:
            save_products(products)
            return {"message": f"Product with id {product_id} deleted successfully"}, 200
        return {"error": "Product not found"}, 404

# Register resources
api.add_resource(ProductList, '/products')
api.add_resource(ProductInStock, '/products/in-stock')
api.add_resource(Product, '/products/<int:product_id>')

if __name__ == '__main__':
    app.run(debug=True) 