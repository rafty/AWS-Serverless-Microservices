from constructs import Construct
from aws_cdk import aws_events


class BasketEventBusConstructor(Construct):

    def __init__(self, scope: "Construct", id: str) -> None:
        super().__init__(scope, id)
        self.name = 'Basket'
        self._eventbus = None
        self._basket_checkout_rule = None
        self._event_source = 'com.basket.basket-checkout'
        self._event_detail_type = 'BasketCheckout'

        self.create_basket_eventbus()

    def create_basket_eventbus(self) -> aws_events.EventBus:

        self._eventbus = aws_events.EventBus(
            self,
            'BasketEventBus',
            event_bus_name=self.name,
        )

        self._basket_checkout_rule = aws_events.Rule(
            self,
            'BasketCheckoutRule',
            rule_name='BasketCheckoutRule',
            description='When Basket microservice checkout the basket',
            event_bus=self._eventbus,
            event_pattern=aws_events.EventPattern(
                source=[self._event_source],
                detail_type=[self._event_detail_type]
            ),
            enabled=True,
        )

    @property
    def eventbus(self) -> aws_events.EventBus:
        return self._eventbus

    @property
    def basket_checkout_rule(self) -> aws_events.Rule:
        return self._basket_checkout_rule

    @property
    def event_source(self):
        return self._event_source

    @property
    def event_detail_type(self):
        return self._event_detail_type
