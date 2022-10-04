from boto3.dynamodb.types import TypeSerializer
from boto3.dynamodb.types import TypeDeserializer


def python_obj_to_dynamodb_obj(python_obj: dict) -> dict:
    print('::python_obj_to_dynamodb_obj()')
    serializer = TypeSerializer()
    return {k: serializer.serialize(v) for k, v in python_obj.items()}


def dynamo_obj_to_python_obj(dynamo_obj: dict) -> dict:
    print('::dynamo_obj_to_python_obj()')
    print(f'dynamo_obj: {dynamo_obj}, type: {type(dynamo_obj)}')
    deserializer = TypeDeserializer()

    # return {k: deserializer.deserialize(v) for k, v in dynamo_obj.items()}
    # Todo: ↑↑↑↑ 何故かうまくいかない。json map listがあるとだめなようだ。
    # Todo: ↑↑↑↑ productではうまくいってる。dictのnestがあると上記ではだめなようだ。
    # Todo: {key: deserializer.deserialize(dynamo_obj[key]) for key in dynamo_obj }
    # result = {}
    # for key in dynamo_obj:
    #     print(f'key: {key}, value: {dynamo_obj[key]}')
    #     result[key] = deserializer.deserialize(dynamo_obj[key])
    # Todo: ↓↓↓↓ のようにすればうまくいった。
    result = {key: deserializer.deserialize(dynamo_obj[key]) for key in dynamo_obj }

    return result
