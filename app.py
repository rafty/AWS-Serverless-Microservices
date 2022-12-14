#!/usr/bin/env python3
import os
import aws_cdk as cdk
from stacks.product_service_stack import ProductServiceStack
from stacks.basket_service_stack import BasketServiceStack
from stacks.order_service_stack import OrderServiceStack


env = cdk.Environment(
    account=os.environ.get("CDK_DEPLOY_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"]),
    region=os.environ.get("CDK_DEPLOY_REGION", os.environ["CDK_DEFAULT_REGION"]),
)

app = cdk.App()

# ProductServiceStack(app, "ProductServiceStack", env=env)

basket_service_stack = BasketServiceStack(app, "BasketServiceStack", env=env)

order_service_stack = OrderServiceStack(app, "OrderServiceStack", env=env)
order_service_stack.add_dependency(basket_service_stack)

app.synth()
