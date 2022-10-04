import json
from service_layer import handlers
from json_encoder import JSONEncoder


class UnsupportedRoute(Exception):
    pass


def lambda_handler(event, context):
    """bodyはJSON stringであることに注意
        {
            "resource": "/product",
            "path": "/product/",
            "httpMethod": "POST",
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
                "Content-Type": "application/json",
                "Host": "a8ixvw1s12.execute-api.ap-northeast-1.amazonaws.com",
                "Postman-Token": "3e68ae33-343a-479b-ac46-bf60a3a41ae0",
                "User-Agent": "PostmanRuntime/7.29.2",
                "Via": "1.1 1552ec44a4dff59a6288644bee85e4a8.cloudfront.net (CloudFront)",
                "X-Amz-Cf-Id": "YC_UZhKPwlk26Ksqj49yCHOFxHH7KUwErZpZIWuCv4-zap53h_gKJA==",
                "X-Amzn-Trace-Id": "Root=1-633aab05-20d4363e0774c4876d267bd0",
                "X-Forwarded-For": "60.116.89.182, 70.132.51.151",
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
                "Content-Type": [
                    "application/json"
                ],
                "Host": [
                    "a8ixvw1s12.execute-api.ap-northeast-1.amazonaws.com"
                ],
                "Postman-Token": [
                    "3e68ae33-343a-479b-ac46-bf60a3a41ae0"
                ],
                "User-Agent": [
                    "PostmanRuntime/7.29.2"
                ],
                "Via": [
                    "1.1 1552ec44a4dff59a6288644bee85e4a8.cloudfront.net (CloudFront)"
                ],
                "X-Amz-Cf-Id": [
                    "YC_UZhKPwlk26Ksqj49yCHOFxHH7KUwErZpZIWuCv4-zap53h_gKJA=="
                ],
                "X-Amzn-Trace-Id": [
                    "Root=1-633aab05-20d4363e0774c4876d267bd0"
                ],
                "X-Forwarded-For": [
                    "60.116.89.182, 70.132.51.151"
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
                "resourceId": "d2eqwm",
                "resourcePath": "/product",
                "httpMethod": "POST",
                "extendedRequestId": "Za-o8HGqtjMF0jw=",
                "requestTime": "03/Oct/2022:09:27:33 +0000",
                "path": "/prod/product/",
                "accountId": "338456725408",
                "protocol": "HTTP/1.1",
                "stage": "prod",
                "domainPrefix": "a8ixvw1s12",
                "requestTimeEpoch": 1664789253810,
                "requestId": "47e5f6f8-0039-4b35-b0a4-9445457c7d57",
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
                "domainName": "a8ixvw1s12.execute-api.ap-northeast-1.amazonaws.com",
                "apiId": "a8ixvw1s12"
            },
            "body": "{\n  \"name\": \"IPone X\",\n  \"description\": \"This is the company's biggest change to its flagship smartphone in years. It includes a borderless.\",\n  \"imageFile\": \"product-1.png\",\n  \"category\": \"Phone\",\n  \"price\": 950.4\n}",
            "isBase64Encoded": false
        }
    """

    print(json.dumps(event))

    http_method = event.get('httpMethod')
    query_string_parameters = event.get('queryStringParameters')
    path_parameters = event.get('pathParameters')

    try:
        if http_method == 'GET':
            if query_string_parameters is not None:
                """ GET product/1234?category=Phone """
                body = handlers.get_product_by_category(
                    prodict_id=path_parameters.get('id'),
                    category=query_string_parameters.get('category')
                )

            elif path_parameters is not None:
                """ GET product/{id} """
                body = handlers.get_product(product_id=path_parameters.get('id'))
            else:
                """ GET product """
                body = handlers.get_all_products()

        elif http_method == 'POST':
            """ POST /product """
            body = handlers.create_product(request=event.get('body'))

        elif http_method == 'PUT':
            """ PUT /product/{id} """
            body = handlers.update_product(product_id=path_parameters.get('id'),
                                           request=event.get('body'))

        elif http_method == 'DELETE':
            """ DELETE /product/{id} """
            body = handlers.delete_product(path_parameters.get('id'))

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

    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Failed to perform operation.',
                'errorMsg': str(e),
            })
        }
