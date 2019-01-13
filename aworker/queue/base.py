from aworker.serializers import BaseSerializer


class RawTask(object):
    def __init__(self, queue_message, task_info):
        self.queue_message = queue_message
        self.task_info = task_info


class BaseQueue(object):
    string_encode_tasks = False
    default_serializer_class = None

    def __init__(self, config=None, serializer=None):
        self.config = config or dict()
        self.serializer = serializer or self.default_serializer_class()
        self.config = config
        self.exit_receiver = False
        assert isinstance(self.serializer, BaseSerializer)

    def send_task(self, task_info):
        raise NotImplementedError()

    def task_receiver(self, output_queue):
        """
        Thread target that receives messages from a queue and passes a RawTask() object to a Queue() for processing.
        The task processor will be watching the Queue() for work.

        :param output_queue: Queue() for passing received tasks out to worker
        :return:
        """
        raise NotImplementedError()

    async def task_ack(self, raw_task):
        """
        Async safe function to acknowledge messages. If this function needs to block at all then the subclass
        implementer is must handle non-blocking considerations
        :param raw_task:
        :return:
        """
        raise NotImplementedError()
