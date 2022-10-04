from constructs import Construct
from aws_cdk import aws_lambda


class BasketFunctionConstructor(Construct):

    def __init__(self, scope: "Construct", id: str, props: dict) -> None:
        super().__init__(scope, id)
        self.props = props
        self._function = self.create_basket_function()

    def create_basket_function(self) -> aws_lambda.Function:

        function = aws_lambda.Function(
            self,
            'BasketFunction',
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler='lambda_function.lambda_handler',
            code=aws_lambda.Code.from_asset('lambdas/basket'),
            environment={
                'PRIMARY_KEY': 'userName',
                'DYNAMODB_TABLE_NAME': self.props['table'].table_name,
                'EVENT_BUS_NAME': self.props['event_bus_name'],
                'EVENT_SOURCE':  self.props['event_source'],
                'EVENT_DETAIL_TYPE': self.props['event_detail_type'],
            }
        )
        return function

    @property
    def function(self) -> aws_lambda.IFunction:
        return self._function
