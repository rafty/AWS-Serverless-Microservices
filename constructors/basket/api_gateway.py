from constructs import Construct
from aws_cdk import aws_apigateway


class BasketApiConstructor(Construct):

    def __init__(self, scope: "Construct", id: str, props: dict) -> None:
        super().__init__(scope, id)

        self.api: aws_apigateway.LambdaRestApi = None
        self.props = props
        self.basket_api()

    def basket_api(self) -> None:
        self.api = aws_apigateway.LambdaRestApi(
            self,
            'BasketApi',
            handler=self.props['function'],
            proxy=False
        )
        self.rest_resource_and_method()

    def rest_resource_and_method(self) -> None:
        """
        Resource and Method

            /basket
                - GET           : fetch baskets
                - POST          : create basket

            /basket/{userName}
                - GET           : fetch single basket
                - DELETE        : delete basket

            /basket/checkout
                - POST          : checkout basket
                                : expected request payload : { userName : swn }

        """
        basket = self.api.root.add_resource('basket')
        basket.add_method('GET')
        basket.add_method('POST')

        single_basket = basket.add_resource('{userName}')
        single_basket.add_method('GET')
        single_basket.add_method('DELETE')

        basket_checkout = basket.add_resource('checkout')
        basket_checkout.add_method('POST')
