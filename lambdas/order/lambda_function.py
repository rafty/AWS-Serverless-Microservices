import json
import decimal
from service_layer import handlers
from json_encoder import JSONEncoder
from service_layer.handlers import OrderError
"""
GET     /order             Fetch all orders

GET     /order/{userName}  Fetch some order
  - expected request : /order/{userName}?orderDate=timestamp
  - query parameters and filter to dynamo db
"""


class UnsupportedRoute(Exception):
    pass


def sqs_invocation(event: dict):
    print(f'sqs_invocation() - event: {event}')
    """
    {
        "Records": [
            {
                "messageId": "cd5af2a0-d304-46cb-999d-01a9078149fc",
                "receiptHandle": "AQEBKuOkQkStPn/tyIHo+vZHkYG3j2DCPe7dESzkV73e+Ic8maPbC/8IKcNkKgHuq0EKM7BtRyIVdFYVWL+3DCcHsDRNyk5zwvKjuh6iU3ysptrv+vW0ZuBgPgfhjLGl9YoBdjJRueFl+J1cczfjoMrrXZwRssR89vqQ5n7Aw+Ny+qzK2k1zU60RXRDMxxe1UrTwe9pVc3W0sh38eJfkPAwemjsSlREc+Z5OV0p30iPbLWUqmrlvbwYtyaZ7IrqdmC3XfdeJMeS4surBb1inZ8/4I04oLfdBOvvPOYq/wVC9Kk0ubKznDBGoQ2TVzwNKjtrsyGEW2G34feR1ebia53nk9X3oeGW3ch1P1SyyQgkkgEZhZnn7umUoPWgbte4A5pPyyPEo1N8W48UDg7nir6qnKw==",
                "body": "{\"version\":\"0\",\"id\":\"936abaf2-1462-9aef-f536-394ebb8ddf87\",\"detail-type\":\"BasketCheckout\",\"source\":\"com.basket.basket-checkout\",\"account\":\"338456725408\",\"time\":\"2022-10-05T12:55:25Z\",\"region\":\"ap-northeast-1\",\"resources\":[],\"detail\":{\"userName\":\"swn\",\"totalPrice\":0,\"lastName\":\"mehmet\",\"email\":\"ezozkme@gmail.com\",\"address\":\"istanbul\",\"cardInfo\":\"5554443322\",\"paymentMethod\":1,\"total_price\":1820.0,\"items\":{\"userName\":\"swn\",\"items\":[{\"quantity\":2.0,\"color\":\"Red\",\"productId\":\"7934e4bd-d688-4376-bd98-8278b911eaaf\",\"price\":950.0,\"productName\":\"IPhone X\"},{\"quantity\":1.0,\"color\":\"Blue\",\"productId\":\"ab4797a9-cdfa-4158-9da4-82307d76b209\",\"price\":870.0,\"productName\":\"Samsung 10\"}]}}}",
                "attributes": {
                    "ApproximateReceiveCount": "6",
                    "SentTimestamp": "1664974525695",
                    "SenderId": "AIDAIVNDY5GZ7FOG4K4K2",
                    "ApproximateFirstReceiveTimestamp": "1664974525695"
                },
                "messageAttributes": {},
                "md5OfBody": "da13378c352b0d31229746b72a198f1f",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:ap-northeast-1:338456725408:OrderQueue",
                "awsRegion": "ap-northeast-1"
            }
        ]
    }
    """
    """
    ↑　body (json string を dictに変換したもの)
    {	
        "version":"0",
        "id":"936abaf2-1462-9aef-f536-394ebb8ddf87",
        "detail-type":"BasketCheckout",
        "source":"com.basket.basket-checkout",
        "account":"338456725408",
        "time":"2022-10-05T12:55:25Z",
        "region":"ap-northeast-1",
        "resources":[],
        "detail":{
            "userName":"swn",
            "totalPrice":0,"lastName":"mehmet",
            "email":"ezozkme@gmail.com",
            "address":"istanbul",
            "cardInfo":"5554443322",
            "paymentMethod":1,
            "total_price":1820.0,
            "items":{
                "userName":"swn",
                "items":[
                    {
                        "quantity":2.0,
                        "color":"Red",
                        "productId":"7934e4bd-d688-4376-bd98-8278b911eaaf",
                        "price":950.0,
                        "productName":"IPhone X"
                    },
                    {
                        "quantity":1.0,
                        "color":"Blue",
                        "productId":"ab4797a9-cdfa-4158-9da4-82307d76b209",
                        "price":870.0,
                        "productName":"Samsung 10"
                    }
                ]
            }
        }
    }    
    """

    for record in event['Records']:
        # expected record :
        # { "detail-type": "CheckoutBasket",
        #   "source": "com.basket.checkoutbasket",
        #   "detail": { "userName": "swn", "totalPrice": 1820, ・・・}
        print(f'record: {record}')

        basket_checkout_event = record.get('body', {})  # body: json string
        # handlers.create_order(request.get('detail'))
        handlers.create_order(basket_checkout_event)
    return


def apigateway_invocation(event: dict):
    print(f'apigateway_invocation() - event: {event}')

    try:
        http_method = event.get('httpMethod')
        query_string_parameters = event.get('queryStringParameters')
        path_parameters = event.get('pathParameters')
        path = event.get('path')

        if http_method == 'GET':
            if path_parameters is not None:
                """ GET order/{userName}?orderDate={datetime} """
                body = handlers.get_order(
                    user_name=path_parameters.get('userName'),
                    order_date=query_string_parameters.get('orderDate')
                )
            else:
                """ GET all orders """
                body = handlers.get_all_orders()
        else:
            raise UnsupportedRoute(f'Unsupported Route :{http_method}')

        print(f'return body: {body}')
        response = {
            'statusCode': 200,
            'body': json.dumps(
                        {
                            'message': f'Successfully finished operation: {http_method}',
                            'body': body,
                        },
                        cls=JSONEncoder)
        }
        print(f'return response: {response}')
        return response

    except UnsupportedRoute as e:
        print(str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': str(e),
            })
        }

    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Failed to perform operation.',
                'errorMsg': str(e),
            })
        }


def lambda_handler(event, context):
    """bodyはJSON stringであることに注意
    {
        "resource": "/order",
        "path": "/basket",
        "httpMethod": "GET",
        "headers": {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "CloudFront-Forwarded-Proto": "https",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-Mobile-Viewer": "false",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Tablet-Viewer": "false",
            "CloudFront-Viewer-ASN": "17676",
            "CloudFront-Viewer-Country": "JP",
            "Host": "j9hyeuq7ie.execute-api.ap-northeast-1.amazonaws.com",
            "Postman-Token": "d957ecae-10a1-42b2-83b6-91a96f97df46",
            "User-Agent": "PostmanRuntime/7.29.2",
            "Via": "1.1 184ecda2873f0021882d1dce6dffe53e.cloudfront.net (CloudFront)",
            "X-Amz-Cf-Id": "LbZCEwSdGhP6olvjlXsXvGq8XVmZ3_ZQ9AEvSkMxTYSV7mqNJ_wwSQ==",
            "X-Amzn-Trace-Id": "Root=1-633be6df-514439fe71cda1852eb7c4da",
            "X-Forwarded-For": "60.116.89.182, 130.176.217.182",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https"
        },
        "multiValueHeaders": {
            "Accept": [
                "*/*"
            ],
            "Accept-Encoding": [
                "gzip, deflate, br"
            ],
            "CloudFront-Forwarded-Proto": [
                "https"
            ],
            "CloudFront-Is-Desktop-Viewer": [
                "true"
            ],
            "CloudFront-Is-Mobile-Viewer": [
                "false"
            ],
            "CloudFront-Is-SmartTV-Viewer": [
                "false"
            ],
            "CloudFront-Is-Tablet-Viewer": [
                "false"
            ],
            "CloudFront-Viewer-ASN": [
                "17676"
            ],
            "CloudFront-Viewer-Country": [
                "JP"
            ],
            "Host": [
                "j9hyeuq7ie.execute-api.ap-northeast-1.amazonaws.com"
            ],
            "Postman-Token": [
                "d957ecae-10a1-42b2-83b6-91a96f97df46"
            ],
            "User-Agent": [
                "PostmanRuntime/7.29.2"
            ],
            "Via": [
                "1.1 184ecda2873f0021882d1dce6dffe53e.cloudfront.net (CloudFront)"
            ],
            "X-Amz-Cf-Id": [
                "LbZCEwSdGhP6olvjlXsXvGq8XVmZ3_ZQ9AEvSkMxTYSV7mqNJ_wwSQ=="
            ],
            "X-Amzn-Trace-Id": [
                "Root=1-633be6df-514439fe71cda1852eb7c4da"
            ],
            "X-Forwarded-For": [
                "60.116.89.182, 130.176.217.182"
            ],
            "X-Forwarded-Port": [
                "443"
            ],
            "X-Forwarded-Proto": [
                "https"
            ]
        },
        "queryStringParameters": null,
        "multiValueQueryStringParameters": null,
        "pathParameters": null,
        "stageVariables": null,
        "requestContext": {
            "resourceId": "3ufqri",
            "resourcePath": "/basket",
            "httpMethod": "GET",
            "extendedRequestId": "ZeEDAF_FNjMF0DQ=",
            "requestTime": "04/Oct/2022:07:55:11 +0000",
            "path": "/prod/basket",
            "accountId": "338456725408",
            "protocol": "HTTP/1.1",
            "stage": "prod",
            "domainPrefix": "j9hyeuq7ie",
            "requestTimeEpoch": 1664870111836,
            "requestId": "5a6a585d-74aa-421a-8601-b663e5e60f95",
            "identity": {
                "cognitoIdentityPoolId": null,
                "accountId": null,
                "cognitoIdentityId": null,
                "caller": null,
                "sourceIp": "60.116.89.182",
                "principalOrgId": null,
                "accessKey": null,
                "cognitoAuthenticationType": null,
                "cognitoAuthenticationProvider": null,
                "userArn": null,
                "userAgent": "PostmanRuntime/7.29.2",
                "user": null
            },
            "domainName": "j9hyeuq7ie.execute-api.ap-northeast-1.amazonaws.com",
            "apiId": "j9hyeuq7ie"
        },
        "body": null,
        "isBase64Encoded": false
    }
    """

    print(json.dumps(event))
    if event.get('Records', None):
        # SQS Invocation
        sqs_invocation(event)

    elif event.get('detail-type', None):
        # Event Bridge Invocation
        # 今回はEventBridgeからLambdaの呼び出しは無い
        pass
    else:
        return apigateway_invocation(event)

