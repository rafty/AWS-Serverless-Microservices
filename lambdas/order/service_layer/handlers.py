import os
import json
import uuid
import decimal
import datetime
import boto3
# from dynamo_obj_conversion import python_obj_to_dynamodb_obj
# from dynamo_obj_conversion import dynamo_obj_to_python_obj
from service_layer.dynamo_obj_conversion import python_obj_to_dynamodb_obj
from service_layer.dynamo_obj_conversion import dynamo_obj_to_python_obj
from json_encoder import JSONEncoder

table_name = os.environ.get('DYNAMODB_TABLE_NAME')
primary_key = os.environ.get('PRIMARY_KEY')
sort_key = os.environ.get('SORT_KEY')

dynamodb = boto3.client('dynamodb')


class NeedParameter(Exception):
    pass


class OrderError(Exception):
    pass


# def create_order(basket_checkout_event: str):
def create_order(basket_checkout_event: str):
    # Todo: basket_checkout_eventの中身はjsonで・・・
    # Todo: outputの中身はdictで・・・
    # create order item into db
    # detail object should be basket_checkout_event json object
    print(f'::create_order() type: {type(basket_checkout_event)}\nbasket_checkout_event: {basket_checkout_event}')
    """
    json string
    {
        "version": "0",
        "id": "63a9ea27-9eac-3f93-323e-702b59b721e8",
        "detail-type": "BasketCheckout",
        "source": "com.basket.basket-checkout",
        "account": "338456725408",
        "time": "2022-10-05T14:00:28Z",
        "region": "ap-northeast-1",
        "resources": [],
        "detail": {
            "userName": "swn",
            "totalPrice": 0,
            "lastName": "mehmet",
            "email": "ezozkme@gmail.com",
            "address": "istanbul",
            "cardInfo": "5554443322",
            "paymentMethod": 1,
            "total_price": 1820,
            "items": {
                "userName": "swn",
                "items": [
                    {
                        "quantity": 2,
                        "color": "Red",
                        "productId": "7934e4bd-d688-4376-bd98-8278b911eaaf",
                        "price": 950,
                        "productName": "IPhone X"
                    },
                    {
                        "quantity": 1,
                        "color": "Blue",
                        "productId": "ab4797a9-cdfa-4158-9da4-82307d76b209",
                        "price": 870,
                        "productName": "Samsung 10"
                    }
                ]
            }
        }
    }    
    """

    try:
        # Todo: jsonにFloatが含まれるためDecimalをつかう
        event_data = json.loads(basket_checkout_event, parse_float=decimal.Decimal)
        print(f'event_data dict: {event_data}')
        """
        type: dict
        {
            'version': '0',
            'id': '63a9ea27-9eac-3f93-323e-702b59b721e8',
            'detail-type': 'BasketCheckout',
            'source': 'com.basket.basket-checkout',
            'account': '338456725408',
            'time': '2022-10-05T14:00:28Z',
            'region': 'ap-northeast-1',
            'resources': [],
            'detail': {
                'userName': 'swn',
                'totalPrice': 0,
                'lastName': 'mehmet',
                'email': 'ezozkme@gmail.com',
                'address': 'istanbul',
                'cardInfo': '5554443322',
                'paymentMethod': 1,
                'total_price': Decimal('1820.0'),
                'items': {
                    'userName': 'swn',
                    'items': [
                        {
                            'quantity': Decimal('2.0'),
                            'color': 'Red',
                            'productId': '7934e4bd-d688-4376-bd98-8278b911eaaf',
                            'price': Decimal('950.0'),
                            'productName': 'IPhone X'
                        },
                        {
                            'quantity': Decimal('1.0'),
                            'color': 'Blue',
                            'productId': 'ab4797a9-cdfa-4158-9da4-82307d76b209',
                            'price': Decimal('870.0'),
                            'productName': 'Samsung 10'
                        }
                    ]
                }
            }
        }
        """
        detail = event_data.get('detail')
        # orderDateを追加
        detail['orderDate'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        print(f'detail: {detail}')
        """
        {
            'userName': 'swn',
            'totalPrice': 0,
            'lastName': 'mehmet',
            'email': 'ezozkme@gmail.com',
            'address': 'istanbul',
            'cardInfo': '5554443322',
            'paymentMethod': 1,
            'total_price': Decimal('1820.0'),
            'items': {
                'userName': 'swn',
                'items': [
                    {
                        'quantity': Decimal('2.0'),
                        'color': 'Red',
                        'productId': '7934e4bd-d688-4376-bd98-8278b911eaaf',
                        'price': Decimal('950.0'),
                        'productName': 'IPhone X'
                    },
                    {
                        'quantity': Decimal('1.0'),
                        'color': 'Blue',
                        'productId': 'ab4797a9-cdfa-4158-9da4-82307d76b209',
                        'price': Decimal('870.0'),
                        'productName': 'Samsung 10'
                    }
                ]
            },
            'orderDate': '2022-10-05T14:00:29Z'
        }
        """

        # (注)floatはDecimal()でput_item()する。
        resp = dynamodb.put_item(
            TableName=table_name,
            Item=python_obj_to_dynamodb_obj(detail)
        )
        print(f'put_item() resp: {json.dumps(resp)}')
        return resp
    except Exception as e:
        print(str(e))
        raise Exception


def get_order(user_name: str, order_date: str) -> dict:
    # Todo: outputの中身はdictで・・・
    # Todo: get_itemのresponse: Item
    print(f'::get_order() user_name: {user_name}, order_date: {order_date})')
    try:
        resp = dynamodb.query(
            TableName=table_name,
            KeyConditionExpression="userName = :userName AND orderDate = :orderDate",
            ExpressionAttributeValues={
                ':userName': {'S': user_name},
                ':orderDate': {'S': order_date}
            }
        )
        print(f'query() resp: {resp}')
        orders = resp.get('Items', {})
        deserialized_order_list = [dynamo_obj_to_python_obj(order) for order in orders]
        return deserialized_order_list

    except Exception as e:
        print(str(e))
        raise Exception


def get_all_orders():
    # Todo: outputの中身はdictで・・・
    # Todo: scanのresponse: Items
    print('::get_all_orders()')
    try:
        resp = dynamodb.scan(
            TableName=table_name,
        )
        orders = resp['Items']
        print(f"resp['Items']: {json.dumps(orders)}")
        order_list = [dynamo_obj_to_python_obj(order) for order in orders]
        return order_list

    except Exception as e:
        print(str(e))
        raise Exception
