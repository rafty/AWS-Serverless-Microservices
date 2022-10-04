from aws_cdk import Stack
from constructs import Construct
from constructors.product.dynamodb import ProductTableConstructor
from constructors.product.function import ProductFunctionConstructor
from constructors.product.api_gateway import ProductApiConstructor


class ProductServiceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        product_table = ProductTableConstructor(self, 'ProductTableConstructor')

        product_function = ProductFunctionConstructor(
            self,
            'LambdaFunctionConstructor',
            prop={
                # 'table_name': product_table.name,
                'table': product_table.table
            }
        )

        product_api = ProductApiConstructor(
            self,
            'ProductApiConstructor',
            prop={
                'function': product_function.function
            }
        )

