import pytest
import requests
import json

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    # Setup: Ensure the server is running and create initial data
    # In a real-world scenario, you might start the server here
    # and create a fresh database.
    # For now, we assume the server is running and the DB is clean.

    # Teardown: Clean up created resources
    yield
    # You might want to clean up the database after tests run
    pass

def test_get_root():
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert response.json() == {"message": "Restaurant POS API running 🚀"}

def test_create_menu_items():
    items = [
        {"name": "Margherita Pizza Test", "price": 12.5, "category": "pizza"},
        {"name": "Caesar Salad", "price": 8.9, "category": "salad"},
        {"name": "Cola", "price": 3.0, "category": "drink"}
    ]
    for item in items:
        response = requests.post(f"{BASE_URL}/menu/", json=item)
        assert response.status_code == 200
        assert response.json()["name"] == item["name"]

def test_list_all_menu_items():
    response = requests.get(f"{BASE_URL}/menu/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3

def test_create_order():
    order_data = {
        "items": [
            {"menu_item_id": 1, "quantity": 2},
            {"menu_item_id": 3, "quantity": 1}
        ]
    }
    response = requests.post(f"{BASE_URL}/orders/", json=order_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert len(data["items"]) == 2

def test_get_all_orders():
    response = requests.get(f"{BASE_URL}/orders/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1

def test_get_single_order():
    response = requests.get(f"{BASE_URL}/orders/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1

def test_replace_order():
    order_data = {
        "status": "completed",
        "items": [
            {"menu_item_id": 2, "quantity": 1},
            {"menu_item_id": 3, "quantity": 2}
        ]
    }
    response = requests.put(f"{BASE_URL}/orders/1", json=order_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"

def test_partially_update_order():
    update_data = {"status": "cancelled"}
    response = requests.patch(f"{BASE_URL}/orders/1", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelled"

def test_delete_order():
    response = requests.delete(f"{BASE_URL}/orders/1")
    assert response.status_code == 200
    assert response.json() == {"message": "Order 1 deleted successfully"}

def test_create_order_with_invalid_item():
    order_data = {"items": [{"menu_item_id": 999, "quantity": 1}]}
    response = requests.post(f"{BASE_URL}/orders/", json=order_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Menu item 999 not found"}