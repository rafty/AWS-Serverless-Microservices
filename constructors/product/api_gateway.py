import aws_cdk
from constructs import Construct
from aws_cdk import aws_apigateway


class ProductApiConstructor(Construct):

    def __init__(self, scope: "Construct", id: str, prop: dict) -> None:
        super().__init__(scope, id)

        self.api: aws_apigateway.LambdaRestApi = None
        self.prop = prop
        self.product_api()

    def product_api(self) -> None:
        self.api = aws_apigateway.LambdaRestApi(
            self,
            'ProductApi',
            handler=self.prop['function'],
            proxy=False
        )
        self.rest_resource_and_method()

    def rest_resource_and_method(self) -> None:
        """
        Resource and Method
            /product
                - GET       : fetch all products
                - POST      : create product

            /product/{id}
                - GET       : fetch single product
                - PUT       : update product
                - DELETE    : delete product
        """
        product = self.api.root.add_resource('product')
        product.add_method('GET')
        product.add_method('POST')

        single_product = product.add_resource('{id}')
        single_product.add_method('GET')
        single_product.add_method('PUT')
        single_product.add_method('DELETE')
