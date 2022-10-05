import aws_cdk
from constructs import Construct
from aws_cdk import aws_sqs


class OrderQueueConstructor(Construct):

    def __init__(self, scope: "Construct", id: str) -> None:
        super().__init__(scope, id)
        self.name = 'OrderQueue'
        self._queue = self.create_sqs_queue()

    def create_sqs_queue(self) -> aws_sqs.Queue:
        queue = aws_sqs.Queue(
            self,
            'OrderQueue',
            queue_name=self.name,
            visibility_timeout=aws_cdk.Duration.seconds(30)
        )
        return queue

    @property
    def queue(self):
        return self._queue

    # Todo: addEventSource
    # addEventSource(
    #     SqsEventSource(
    #         self.orderQueue,
    #         {'batchSize': 1}
    #     )
    # );

