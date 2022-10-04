import os
import json
import uuid
import decimal
import boto3
from boto3.dynamodb.types import TypeSerializer
from boto3.dynamodb.types import TypeDeserializer


table_name = os.environ.get('DYNAMODB_TABLE_NAME')

# Todo: DynamoDBのAPIでは
# Todo: transactionやConditionExpressionなどを使いたいので、
# Todo: boto3.clientの低レイヤーを使用する。
dynamodb = boto3.client('dynamodb')

# Todo: boto3.clientの低レイヤーを使用すると
# Todo: DynamoDBのitemは、DynamoDB Objectは以下の構成になるので、
# Todo: python_obj_to_dynamodb_obj()やdynamo_obj_to_python_obj()を使う
"""item = {
  "Author": {"S": "富田鈴花"},
  "Authorcode": {"S": "15"},
  "Blogkey": {"N": "30775"},
  "Entrydate": {"N": "201909062231"},
  "Images": {"L": [
      {"S":"https://cdn.hinatazaka46.com/files/14/diary/official/member/moblog/201909/mobzVcYf5.jpg"},
      {"S": "https://cdn.hinatazaka46.com/files/14/diary/official/member/moblog/201909/mobbmdhGD.jpg"},
      {"S": "https://cdn.hinatazaka46.com/files/14/diary/official/member/moblog/201909/mobNBUyrd.jpg"}
    ]
  },
  "Title": {"S": "東北自動車道"},
  "Url": {"S": "https://www.hinatazaka46.com/s/official/diary/detail/30775?ima=0000&cd=member"}
}"""




# Todo: 低レベルAPI [boto3.client('dynamodb')]のために
# Todo: TypeSerializer, TypeDeserializerを使う
def python_obj_to_dynamodb_obj(python_obj: dict) -> dict:
    print('python_obj_to_dynamodb_obj()')
    serializer = TypeSerializer()
    return {k: serializer.serialize(v) for k, v in python_obj.items()}


def dynamo_obj_to_python_obj(dynamo_obj: dict) -> dict:
    print('dynamo_obj_to_python_obj()')
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in dynamo_obj.items()}


def get_product(product_id: str):
    # Todo: outputの中身はdictで・・・
    # Todo: get_itemのresponse: Item

    print(f'get_product({product_id})')
    try:

        resp = dynamodb.get_item(
            TableName=table_name,
            Key=python_obj_to_dynamodb_obj({'id': product_id})  # {'id': {'S': 'aaa-bbb-ccc-ddd'}}
        )

        # product = resp.get('Item', {})  # Todo: Itemがなければ{}を返す
        product = resp['Item']
        print(f'Product: {str(product)}')

        # Todo: Deserialize
        deserialized_product = dynamo_obj_to_python_obj(product)

        return deserialized_product

    except Exception as e:
        print(str(e))
        raise Exception


def get_all_products():
    # Todo: outputの中身はdictで・・・
    # Todo: scanのresponse: Items

    print('get_all_products()')
    try:
        resp = dynamodb.scan(
            TableName=table_name,
        )
        products = resp['Items']
        print(f"resp['Items']: {json.dumps(products)}")

        # Todo: list(deserialized_dict)
        product_list = [dynamo_obj_to_python_obj(product) for product in products]

        return product_list

    except Exception as e:
        print(str(e))
        raise Exception


def create_product(request: str):
    # Todo: requestの中身はjsonで・・・
    # Todo: outputの中身はdictで・・・

    print(f'create_product: {request}')

    try:
        # Todo: jsonにFloatが含まれるためDecimalをつかう
        item = json.loads(request, parse_float=decimal.Decimal)
        product_id = str(uuid.uuid4())
        item['id'] = product_id  # Todo: idを追加
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


def delete_product(product_id: str):
    # Todo: outputの中身はdictで・・・

    print(f'delete_product({product_id})')
    try:
        resp = dynamodb.delete_item(
            TableName=table_name,
            # Key={'id': product_id}
            Key=python_obj_to_dynamodb_obj({'id': product_id})  # {'id': {'S': 'aaa-bbb-ccc-ddd'}}
        )
        print(json.dumps(resp))
        return resp

    except Exception as e:
        print(str(e))
        raise Exception


def update_product(product_id: str, request: str):
    # Todo: requestの中身はjsonで・・・
    # Todo: outputの中身はdictで・・・

    print(f'update_product: {json.dumps(request)}')
    try:
        req = json.loads(request, parse_float=decimal.Decimal)
        kv_list = list(req.items())  # [('name', 'IPhone XY'), ('imageFile', 'product-1Y.png')]
        key_list = [k for k, v in kv_list]  # ['name', 'imageFile']

        set_update_expression = 'SET ' + ', '.join([f'#{key} = :{key}' for key in key_list])
        # 'SET #name = :name, #imageFile = :imageFile'

        expression_attribute_name = {}
        for k, v in kv_list:
            expression_attribute_name.update(dict([(f'#{k}', k)]))
        # { '#name': 'name', '#imageFile': 'imageFile' }

        expression_attribute_values = {}
        value = None
        for k, v in kv_list:
            key = f':{k}'
            if type(v) is int:
                value = {'N': v}
            if type(v) is str:
                value = {'S': v}
            expression_attribute_values.update(dict([(key, value)]))
        # { ':name': {'S': 'IPhone XY'}, ':imageFile': {'S': 'product-1Y.png'}

        resp = dynamodb.update_item(
            TableName=table_name,
            Key=python_obj_to_dynamodb_obj({'id': product_id}),  # {'id': {'S': 'aaa-bbb-ccc-ddd'}}
            UpdateExpression=set_update_expression,
            ExpressionAttributeNames=expression_attribute_name,
            ExpressionAttributeValues=expression_attribute_values,
            # ReturnValues="ALL_NEW"  # Todo
        )
        print(json.dumps(resp))
        return resp

    except Exception as e:
        print(str(e))
        raise Exception


# Todo: これは使わない。そもそもPartition Keyだけのテーブルでは要らない。
def get_product_by_category(prodict_id, category):
    # Todo: outputの中身はdictで・・・
    # Todo: queryのresponse: Items

    print(f'get_product_by_category(prodict_id={prodict_id}, category={category})')

    resp = dynamodb.query(
        TableName=table_name,
        KeyConditionExpression="id = :productId",
        FilterExpression='contains (category, :category)',
        ExpressionAttributeValues={
            ':productId': {'S': prodict_id},
            ':category': {'S': category},
        },
        # ScanIndexForward=True  # Todo
    )

    products = resp['Items']
    print(f"resp['Items']: {json.dumps(products)}")

    # Todo: list(deserialized_dict)
    product_list = [dynamo_obj_to_python_obj(product) for product in products]

    return product_list
