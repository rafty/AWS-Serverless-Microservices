from constructs import Construct
from aws_cdk import aws_lambda


class OrderFunctionConstructor(Construct):

    def __init__(self, scope: "Construct", id: str, props: dict) -> None:
        super().__init__(scope, id)
        self.props = props
        self._function = self.create_order_function()

    def create_order_function(self) -> aws_lambda.Function:

        function = aws_lambda.Function(
            self,
            'OrderFunction',
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler='lambda_function.lambda_handler',
            code=aws_lambda.Code.from_asset('lambdas/order'),
            environment={
                'DYNAMODB_TABLE_NAME': self.props['table'].table_name,
                # 'PRIMARY_KEY': 'userName',
                'PRIMARY_KEY': self.props['partition_key'],
                # 'SORT_KEY': 'orderDate',
                'SORT_KEY': self.props['sort_key'],
            }
        )
        return function

    @property
    def function(self) -> aws_lambda.IFunction:
        return self._function
