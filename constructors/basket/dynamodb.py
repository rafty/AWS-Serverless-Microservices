import aws_cdk
from constructs import Construct
from aws_cdk import aws_dynamodb


"""
    // Basket DynamoDb Table Creation
        // basket : PK: userName -- items (SET-MAP object) 
          // item1 - { quantity - color - price - productId - productName }
          // item2 - { quantity - color - price - productId - productName }
"""

class BasketTableConstructor(Construct):

    def __init__(self, scope: "Construct", id: str) -> None:
        super().__init__(scope, id)
        self.name = 'basket'
        self._table = self.create_basket_table()

    def create_basket_table(self) -> aws_dynamodb.Table:
        table = aws_dynamodb.Table(
            self,
            id='BasketDynamodbTable',
            table_name=self.name,
            partition_key=aws_dynamodb.Attribute(name='userName',
                                                 type=aws_dynamodb.AttributeType.STRING),
            removal_policy=aws_cdk.RemovalPolicy.DESTROY,
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST
        )
        return table

    # @property
    # def name(self) -> str:
    #     return self._name

    @property
    def table(self) -> aws_dynamodb.Table:
        return self._table
