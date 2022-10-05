import aws_cdk
from aws_cdk import Stack
from constructs import Construct
from constructors.basket.dynamodb import BasketTableConstructor
from constructors.basket.function import BasketFunctionConstructor
from constructors.basket.api_gateway import BasketApiConstructor
from constructors.basket.eventbus import BasketEventBusConstructor


class BasketServiceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        basket_table = BasketTableConstructor(
            self,
            'BasketTableConstructor'
        )

        basket_eventbus = BasketEventBusConstructor(
            self,
            'BasketEventBusConstructor',
        )

        basket_function = BasketFunctionConstructor(
            self,
            'BasketFunctionConstructor',
            props={
                'table': basket_table.table,
                'event_bus_name': basket_eventbus.eventbus.event_bus_name,
                'event_source': basket_eventbus.event_source,
                'event_detail_type': basket_eventbus.event_detail_type,
            },
        )
        basket_table.table.grant_read_write_data(basket_function.function)
        basket_eventbus.eventbus.grant_put_events_to(basket_function.function)

        basket_api = BasketApiConstructor(
            self,
            'BasketApiConstructor',
            props={
                'function': basket_function.function
            }
        )

        # Event Bridge EventBus ARN
        aws_cdk.CfnOutput(
            self,
            'BasketCheckoutEventBusARN',
            value=basket_eventbus.eventbus.event_bus_arn,
            description='Basket Service checkout eventbus ARN',
            export_name='BasketCheckoutEventBusARN'
        )
        # aws_cdk.CfnOutput(
        #     self,
        #     'BasketCheckoutEventBusRule',
        #     value=basket_eventbus.basket_checkout_rule.rule_arn,
        #     description='Basket Service checkout eventbus rule arn',
        #     export_name='BasketCheckoutEventBusRuleARN'
        # )
