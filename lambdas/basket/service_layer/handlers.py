import os
import json
import uuid
import decimal
import boto3
# from dynamo_obj_conversion import python_obj_to_dynamodb_obj
# from dynamo_obj_conversion import dynamo_obj_to_python_obj
from service_layer.dynamo_obj_conversion import python_obj_to_dynamodb_obj
from service_layer.dynamo_obj_conversion import dynamo_obj_to_python_obj
from json_encoder import JSONEncoder

table_name = os.environ.get('DYNAMODB_TABLE_NAME')
primary_key = os.environ.get('PRIMARY_KEY')
eventbus_name = os.environ.get('EVENT_BUS_NAME')
event_source = os.environ.get('EVENT_SOURCE')
event_detail_type = os.environ.get('EVENT_DETAIL_TYPE')

dynamodb = boto3.client('dynamodb')
eventbus = boto3.client('events')


class NeedParameter(Exception):
    pass


class BasketError(Exception):
    pass


def get_basket(user_name: str) -> dict:
    # Todo: outputの中身はdictで・・・
    # Todo: get_itemのresponse: Item

    print(f'::get_basket({user_name})')
    try:

        resp = dynamodb.get_item(
            TableName=table_name,
            Key=python_obj_to_dynamodb_obj({'userName': user_name})
            # {'userName': {'S': 'Takashi'}}
        )

        print(f'get_item() resp: {resp}')

        # basket = resp['Item']
        basket = resp.get('Item', {})

        deserialized_basket = dynamo_obj_to_python_obj(basket)
        return deserialized_basket

    except Exception as e:
        print(str(e))
        raise Exception


def get_all_baskets():
    # Todo: outputの中身はdictで・・・
    # Todo: scanのresponse: Items

    print('::get_all_baskets()')
    try:
        resp = dynamodb.scan(
            TableName=table_name,
        )
        baskets = resp['Items']
        print(f"resp['Items']: {json.dumps(baskets)}")

        # Todo: list(deserialized_dict)
        basket_list = [dynamo_obj_to_python_obj(basket) for basket in baskets]
        return basket_list

    except Exception as e:
        print(str(e))
        raise Exception


def create_basket(request: str):
    # Todo: requestの中身はjsonで・・・
    # Todo: outputの中身はdictで・・・

    print(f'::create_basket(): {request}')

    try:
        # Todo: jsonにFloatが含まれるためDecimalをつかう
        item = json.loads(request, parse_float=decimal.Decimal)
        print(f'item dict: {item}')

        resp = dynamodb.put_item(
            TableName=table_name,
            Item=python_obj_to_dynamodb_obj(item)
        )
        print(f'put_item() resp: {json.dumps(resp)}')

        return resp

    except Exception as e:
        print(str(e))
        raise Exception


def delete_basket(user_name: str):
    # Todo: outputの中身はdictで・・・

    print(f'::delete_basket(): {user_name}')
    try:
        resp = dynamodb.delete_item(
            TableName=table_name,
            Key=python_obj_to_dynamodb_obj({'userName': user_name})
            # {'userName': {'S': 'Takashi Yagita'}}
        )
        print(json.dumps(resp))
        return resp

    except Exception as e:
        print(str(e))
        raise Exception


def publish_checkout_basket_event(checkout_payload: dict) -> dict:
    print(f'::publish_checkout_basket_event() with payload: {checkout_payload}')
    try:
        response = eventbus.put_events(
            Entries=[
                {
                    'EventBusName': eventbus_name,
                    'Source': event_source,
                    'DetailType': event_detail_type,
                    'Detail': json.dumps(checkout_payload, cls=JSONEncoder),
                    # Todo: 注意 JSONEncoderを入れること
                }
            ],
        )
        print(f'put_event.Detail: {json.dumps(checkout_payload, cls=JSONEncoder)}')
        print(f'EventBridge put_events resp: {response}')
        """
        {
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
        """
        return response

    except Exception as e:
        print(str(e))
        raise Exception


def prepare_order_payload(request: dict, basket: dict) -> dict:
    """
    prepare order payload -> calculate total_price and combine checkoutRequest and basket items
    aggregate and enrich request and basket data in order to create order payload

    basket = {
        "userName" : "swn",
        "items": [
            {
                "quantity": 2,
                "color": "Red",
                "price": 950,
                "productId": "7934e4bd-d688-4376-bd98-8278b911eaaf",
                "productName": "IPhone X"
            },
            {
                "quantity": 1,
                "color": "Blue",
                "price": 870,
                "productId": "ab4797a9-cdfa-4158-9da4-82307d76b209",
                "productName": "Samsung 10"
            }
        ]
    }
    """
    print(f'::prepare_order_payload(): {request}, {basket}')

    try:
        if basket is None or basket.get('items', []) == []:
            raise BasketError(f'No items in basket:')

        total_price = 0
        total_price = sum([item['price'] for item in basket['items']])
        request['total_price'] = total_price
        print(f'checkout basket - total price: {total_price}')

        """copies all properties from basket into checkoutRequest"""
        request['items'] = basket
        print(f'Success prepareOrderPayload: {request}')
        return request

    except Exception as e:
        print(str(e))
        raise Exception


def checkout_basket(request: str) -> None:
    # Todo: outputの中身はdictで・・・
    # Todo: queryのresponse: Items

    print(f'::checkout_basket(): {request}')

    req = json.loads(request, parse_float=decimal.Decimal)
    print(f'req dict: {req}')

    if req.get('userName') is None:
        raise NeedParameter(f'basket should exist in request: {req}')

    """ 1- Get existing basket with items """
    basket = get_basket(req['userName'])
    # deserialized_basket = dynamo_obj_to_python_obj(basket)

    """2- create an event json object with basket items, 
        calculate totalprice, prepare order create json data to send ordering ms"""
    checkout_payload = prepare_order_payload(req, basket)
    # checkout_payload = prepare_order_payload(req, deserialized_basket)

    """3- publish an event to eventbridge
        - this will subscribe by order microservice and start ordering process."""
    publishedEvent = publish_checkout_basket_event(checkout_payload)

    """ 4- remove existing basket """
    delete_basket(checkout_payload['userName'])

    return
