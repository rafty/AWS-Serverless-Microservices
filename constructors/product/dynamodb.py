import aws_cdk
from constructs import Construct
from aws_cdk import aws_dynamodb

"""
    Product DynamoDb Table Creation
    product : PK: id -- name - description - imageFile - price - category
"""


class ProductTableConstructor(Construct):

    def __init__(self, scope: "Construct", id: str) -> None:
        super().__init__(scope, id)
        self.name = 'product'
        self._table = self.create_production_table()

    def create_production_table(self) -> aws_dynamodb.Table:
        table = aws_dynamodb.Table(
            self,
            id='ProductDynamodbTable',
            table_name=self.name,
            partition_key=aws_dynamodb.Attribute(name='id', type=aws_dynamodb.AttributeType.STRING),
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
