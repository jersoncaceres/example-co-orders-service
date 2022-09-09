import datetime
import json
import calendar
from pprint import pprint

from dateutil.relativedelta import relativedelta

from exampleco.models.database import Session
from exampleco.models.database.order_items import OrderItem, OrderItemSchema
from exampleco.models.database.orders import Order
from exampleco.models.database.services import ServiceSchema, Service


# pylint: disable=unused-argument
def get_all_orders(event, context):
    """
    Example function that demonstrates grabbing list or orders from database

    Returns:
        Returns a list of all orders pulled from the database.
    """

    orders = Session.query(Order).filter(Order.status.is_(None)).all()
    orders_list = []
    for order in orders:
        orders_list.append(order.to_json())
    pprint(orders_list)
    response = {"statusCode": 200, "body": json.dumps(orders_list, indent=4, sort_keys=True, default=str)}

    return response


def get_order_by_id(event, context):
    """
    Returns:
        Returns an order by id.
    """
    order_id = event.get("pathParameters").get("id")
    order = Session.query(Order).filter(Order.id == order_id, Order.status.is_(None)).first()
    if order:
        results = order.to_json()
        response = {"statusCode": 200, "body": json.dumps(results, indent=4, sort_keys=True, default=str)}
    else:
        response = {"statusCode": 404, "body": f"No order with id {order_id} found!"}
    return response


def create_order(event, context):
    request = event.get('body')
    if request:
        request = json.loads(request)
    if request.get('description') is None or request.get('service_id') is None:
        return {"statusCode": 400, "body": f"Wrong request"}

    order_data = {}
    order_item_data = {}
    service_ids = []
    if request.get('description'):
        order_data['description'] = request['description']
    if request.get('service_id'):
        if type(request.get('service_id')) is not list:
            service_ids.append(request.get('service_id'))
        else:
            service_ids = request.get('service_id')

    order = Order(**order_data)
    Session.add(order)
    Session.commit()
    Session.refresh(order)
    for service_id in service_ids:
        order_item_data['order_id'] = order.id
        order_item_data['service_id'] = service_id
        order_item = OrderItem(**order_item_data)
        Session.add(order_item)
        Session.commit()

    result = order.to_json()

    response = {"statusCode": 200, "body": json.dumps(result, indent=4, sort_keys=True, default=str)}

    return response


def delete_order(event, context):
    order_id = event.get("pathParameters").get("id")
    order = Session.query(Order).filter(Order.id == order_id, Order.status.is_(None)).first()
    if order is None:
        return {"statusCode": 404, "body": f"No order with id {order_id} is found!"}
    order.status = "deleted"
    Session.commit()
    Session.refresh(order)
    result = order.to_json()

    response = {"statusCode": 200, "body": json.dumps(result, indent=4, sort_keys=True, default=str)}

    return response


def update_order(event, context):
    order_id = event.get("pathParameters").get("id")
    order = Session.query(Order).filter(Order.id == order_id, Order.status.is_(None)).first()
    if order is None:
        return {"statusCode": 404, "body": f"No order with id {order_id} is found!"}
    request = event.get('body')
    if request:
        request = json.loads(request)
    if request.get('description'):
        order.description = request['description']

    order_item_data = {}

    if request.get('service_id'):
        Session.query(OrderItem).filter(OrderItem.order_id == order_id).delete()

        service_ids = []
        if type(request.get('service_id')) is not list:
            service_ids.append(request.get('service_id'))
        else:
            service_ids = request.get('service_id')

        for service_id in service_ids:
            order_item_data['order_id'] = order.id
            order_item_data['service_id'] = service_id
            order_item = OrderItem(**order_item_data)
            Session.add(order_item)
            Session.commit()

    Session.commit()
    Session.refresh(order)
    result = order.to_json()

    response = {"statusCode": 200, "body": json.dumps(result, indent=4, sort_keys=True, default=str)}

    return response


def get_service_by_id(event, context):
    """
    Returns:
        Returns a server by id.
    """
    service_id = event.get("pathParameters").get("id")
    service_schema = ServiceSchema(many=False)
    services = Session.query(Service).filter(Service.id == service_id).first()
    if services:
        results = service_schema.dump(services)
        response = {"statusCode": 200, "body": json.dumps(results)}
    else:
        response = {"statusCode": 404, "body": f"No service with id {service_id} found!"}
    return response


# pylint: disable=unused-argument
def get_all_order_items(event, context):
    """
    Returns:
        Returns a list of all order_items pulled from the database.
    """

    order_items_schema = OrderItemSchema(many=True)
    order_items = Session.query(OrderItem).all()
    results = order_items_schema.dump(order_items)

    response = {"statusCode": 200, "body": json.dumps(results)}

    return response


# pylint: disable=unused-argument
def get_all_services(event, context):
    """
    Returns:
        Returns a list of all services pulled from the database.
    """

    services_schema = ServiceSchema(many=True)
    services = Session.query(Service).all()
    results = services_schema.dump(services)

    response = {"statusCode": 200, "body": json.dumps(results)}

    return response


def count_orders(event, context):
    time_range = event.get('queryStringParameters').get('period')
    if time_range not in ['THIS_YEAR', 'THIS_MONTH', 'THIS_WEEK']:
        return {"statusCode": 400, "body": f"Wrong time range"}
    result = []
    if time_range == 'LAST_WEEK':
        for i in range(6, -1, -1):
            col_date = datetime.date.today() + relativedelta(days=-i)
            print(col_date)
            order = Session.query(Order).filter(
                Order.created_on.between(col_date, col_date + relativedelta(days=1))).count()
            print(order)
            result.append({'date': col_date, 'value': order})
    elif time_range == 'THIS_WEEK':
        today = datetime.date.today()
        weekday = today.weekday()
        range_begin = datetime.date.today() + relativedelta(days=-weekday)
        print(range_begin)
        for i in range(0, 7, 1):
            col_date = range_begin + relativedelta(days=i)
            print(col_date)
            order = Session.query(Order).filter(
                Order.created_on.between(col_date, col_date + relativedelta(days=1))).count()
            print(order)
            result.append({'date': col_date.strftime("%A"), 'value': order})
    elif time_range == 'THIS_MONTH':
        today = datetime.date.today()
        range_begin = today + relativedelta(days=-today.day)
        print(range_begin)
        month_range = calendar.monthrange(today.year, today.month)[1]
        for i in range(1, month_range + 1, 1):
            col_date = range_begin + relativedelta(days=i)
            print(col_date)
            order = Session.query(Order).filter(
                Order.created_on.between(col_date, col_date + relativedelta(days=1))).count()
            print(order)
            result.append({'date': col_date.day, 'value': order})
    elif time_range == 'THIS_YEAR':
        today = datetime.date.today()
        range_begin = datetime.date(today.year, 1, 1)
        print("range_begin", range_begin)
        month_range = calendar.monthrange(today.year, today.month)[1]
        for i in range(0, 12, 1):
            col_date = range_begin + relativedelta(months=i)
            print("range:", col_date, col_date + relativedelta(months=1))
            order = Session.query(Order).filter(
                Order.created_on.between(col_date, col_date + relativedelta(months=1))).count()
            print(order)
            result.append({'date': col_date.strftime("%B"), 'value': order})

    return {"statusCode": 200, "body": json.dumps(result, indent=4, sort_keys=True, default=str)}
