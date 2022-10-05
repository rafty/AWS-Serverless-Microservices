import aws_cdk
from constructs import Construct
from aws_cdk import aws_dynamodb


"""
    Order DynamoDb Table Creation
    order :
    
    PK: userName 
    SK: orderDate 
    - totalPrice
    - firstName
    - lastName
    - email
    - address
    - paymentMethod
    - cardInfo
"""


class OrderTableConstructor(Construct):

    def __init__(self, scope: "Construct", id: str) -> None:
        super().__init__(scope, id)
        self.name = 'order'
        self._partition_key = 'userName'
        self._sort_key = 'orderDate'
        self._table = self.create_order_table()

    def create_order_table(self) -> aws_dynamodb.Table:
        table = aws_dynamodb.Table(
            self,
            id='OrderDynamodbTable',
            table_name=self.name,
            partition_key=aws_dynamodb.Attribute(name=self._partition_key,
                                                 type=aws_dynamodb.AttributeType.STRING),
            sort_key=aws_dynamodb.Attribute(name=self._sort_key,
                                            type=aws_dynamodb.AttributeType.STRING),
            removal_policy=aws_cdk.RemovalPolicy.DESTROY,
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST
        )
        return table

    @property
    def table(self) -> aws_dynamodb.Table:
        return self._table

    @property
    def partition_key(self):
        return self._partition_key

    @property
    def sort_key(self):
        return self._sort_key

