import aws_cdk
from constructs import Construct
from aws_cdk import aws_lambda


class ProductFunctionConstructor(Construct):

    def __init__(self, scope: "Construct", id: str, prop: dict) -> None:
        super().__init__(scope, id)
        self.prop = prop
        self._function = self.create_product_function()

    def create_product_function(self) -> aws_lambda.Function:

        function = aws_lambda.Function(
            self,
            'ProductionFunction',
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            handler='lambda_function.lambda_handler',
            code=aws_lambda.Code.from_asset('lambdas/product'),
            environment={
                'PRIMARY_KEY': 'id',
                # 'DYNAMODB_TABLE_NAME': self.prop['table_name']
                'DYNAMODB_TABLE_NAME': self.prop['table'].table_name
            }
        )

        self.prop['table'].grant_read_write_data(function)
        return function

    @property
    def function(self) -> aws_lambda.IFunction:
        return self._function
