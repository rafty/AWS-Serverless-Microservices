import aws_cdk
from aws_cdk import Stack
from constructs import Construct
from aws_cdk import aws_lambda_event_sources
from aws_cdk import aws_events
from aws_cdk import aws_events_targets
from constructors.order.dynamodb import OrderTableConstructor
from constructors.order.function import OrderFunctionConstructor
from constructors.order.api_gateway import OrderApiGwConstructor
from constructors.order.queue import OrderQueueConstructor


class OrderServiceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --------------------------------------------------------
        # Event Target Queue
        #
        order_queue = OrderQueueConstructor(
            self,
            'OrderQueueConstructor',
        )
        # Cross Stack Import
        #  - "Eventbus" from Basket Service Stack
        #  - create "Eventbus Rule" with Eventbus
        #  - AddTarget( SqsQueue(queue) ) to the rule
        basket_checkout_eventbus_arn = aws_cdk.Fn.import_value('BasketCheckoutEventBusARN')
        eventbus = aws_events.EventBus.from_event_bus_arn(
            self,
            'BasketCheckoutEventBus',
            event_bus_arn=basket_checkout_eventbus_arn
        )

        basket_checkout_rule = aws_events.Rule(
            self,
            'BasketCheckoutRule',
            rule_name='BasketCheckoutRule',
            description='When Basket microservice checkout the basket',
            event_bus=eventbus,
            event_pattern=aws_events.EventPattern(
                source=['com.basket.basket-checkout'],  # <----- 直接入力？
                detail_type=['BasketCheckout']        # <----- 直接入力？
            ),
            enabled=True,
        )
        basket_checkout_rule.add_target(aws_events_targets.SqsQueue(order_queue.queue))

        # --------------------------------------------------------
        # Order DynamoDB Table
        #
        order_table = OrderTableConstructor(
            self,
            'OrderTableConstructor'
        )

        # --------------------------------------------------------
        # AWS Lambda Function
        #
        order_function = OrderFunctionConstructor(
            self,
            'OrderFunctionConstructor',
            props={
                'table': order_table.table,
                'partition_key': order_table.partition_key,
                'sort_key': order_table.sort_key,
            },
        )
        order_table.table.grant_read_write_data(order_function.function)

        order_function.function.add_event_source(
            aws_lambda_event_sources.SqsEventSource(
                queue=order_queue.queue,
                batch_size=1  # 10 ?
            )
        )

        # --------------------------------------------------------
        # API Gateway
        #
        order_api = OrderApiGwConstructor(
            self,
            'OrderApiConstructor',
            props={
                'function': order_function.function
            }
        )


