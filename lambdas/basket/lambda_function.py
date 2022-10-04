import json
from service_layer import handlers
from json_encoder import JSONEncoder
from service_layer.handlers import BasketError
"""
GET     /basket             Fetch all baskets
POST    /basket             Create basket
GET     /basket/{userName}  Fetch some basket
DELETE  /basket/{userName}  Delete some basket
POST    /basket/checkout    Checkout Basket
"""


class UnsupportedRoute(Exception):
    pass


def lambda_handler(event, context):
    """bodyはJSON stringであることに注意
    {
        "resource": "/basket",
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

    http_method = event.get('httpMethod')
    query_string_parameters = event.get('queryStringParameters')
    path_parameters = event.get('pathParameters')
    path = event.get('path')

    try:
        if http_method == 'GET':
            if path_parameters is not None:
                """ GET basket/{userName} """
                body = handlers.get_basket(user_name=path_parameters.get('userName'))
            else:
                """ GET all baskets """
                body = handlers.get_all_baskets()

        elif http_method == 'POST':

            if path == '/basket/checkout':
                """ POST /basket/checkout """
                body = handlers.checkout_basket(request=event.get('body'))
            else:
                """ POST /basket """
                body = handlers.create_basket(request=event.get('body'))

        elif http_method == 'DELETE':
            """ DELETE /basket/{userName} """
            body = handlers.delete_basket(path_parameters.get('userName'))

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
                        cls=JSONEncoder
                    )
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

    except BasketError as e:
        # Todo: なぜかここに来ず、Exceptionの方に行ってしまう。
        print('::BasketError exception handler')
        print(str(e))
        return {
            'statusCode': 400,
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
