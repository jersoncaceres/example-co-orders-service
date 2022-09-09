import json

import pytest
import requests as requests

from exampleco.models.database import Session
from exampleco.models.database.order_items import OrderItem
from exampleco.models.database.orders import Order
from exampleco.models.database.services import Service

baseUrl = "http://localhost:8080"


@pytest.fixture()
def resource():
    print("setup")
    service = Service(
        name="Test service",
        price=5,
        description="Pytest generated service"
    )
    Session.add(service)
    Session.commit()
    Session.refresh(service)
    order = Order(
        description="Test Order",
    )
    Session.add(order)
    Session.commit()
    Session.refresh(order)
    order_item = OrderItem(order_id=order.id, service_id=service.id)
    Session.add(order_item)
    Session.commit()
    Session.refresh(order_item)

    yield (order, service, order_item)
    print("teardown")
    Session.query(OrderItem).filter(OrderItem.order_id == order_item.order_id,
                                    OrderItem.service_id == order_item.service_id).delete()
    Session.commit()
    Session.query(Order).filter(Order.id == order.id).delete()
    Session.commit()
    Session.query(Service).filter(Service.id == service.id).delete()
    Session.commit()


def test_list_orders(resource):
    path = "/orders"
    response = requests.get(url=baseUrl + path)
    responseJson = json.loads(response.text)

    assert response.status_code == 200
    assert type(responseJson) == list
    if len(responseJson) > 0:
        assert all(key in ['created_on', 'description', 'id', 'modified_on', 'service', 'status'] for key in
                   responseJson[0].keys())


def test_get_order_by_id(resource):
    order, service, order_item = resource
    path = f"/orders/{order.id}"
    response = requests.get(url=baseUrl + path)
    responseJson = json.loads(response.text)
    print(responseJson['id'])
    assert response.status_code == 200
    assert type(responseJson) == dict
    assert all(key in ['created_on', 'description', 'id', 'modified_on', 'service', 'status'] for key in
               responseJson.keys())


def test_delete_order(resource):
    order, service, order_item = resource
    path = f"/orders/{order.id}"
    # positive case
    response = requests.delete(url=baseUrl + path)
    responseJson = json.loads(response.text)
    assert response.status_code == 200
    assert responseJson['status'] == 'deleted'
    # negative case
    response = requests.delete(url=baseUrl + path)
    assert response.status_code == 404
    assert response.text == f'No order with id {order.id} is found!'


def test_update_order(resource):
    order, service, order_item = resource
    path = f"/orders/{order.id}"
    data = {
        "description": "test"
    }

    response = requests.put(url=baseUrl + path, data=json.dumps(data))
    responseJson = json.loads(response.text)
    assert response.status_code == 200
    assert responseJson['description'] == data['description']
