from constructs import Construct
from aws_cdk import aws_apigateway


class OrderApiGwConstructor(Construct):

    def __init__(self, scope: "Construct", id: str, props: dict) -> None:
        super().__init__(scope, id)

        self.api: aws_apigateway.LambdaRestApi = None
        self.props = props
        self.order_api()

    def order_api(self) -> None:
        self.api = aws_apigateway.LambdaRestApi(
            self,
            'OrderApi',
            handler=self.props['function'],
            proxy=False
        )
        self.rest_resource_and_method()

    def rest_resource_and_method(self) -> None:
        """
        Resource and Method

            /order
                - GET           : fetch orders

            /order/{userName}
                - GET           : fetch single order

        Expected Request:
            /order/{userName}?orderDate=timestamp

        """
        order = self.api.root.add_resource('order')
        order.add_method('GET')

        single_order = order.add_resource('{userName}')
        single_order.add_method('GET')
