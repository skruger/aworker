import queue
from unittest import TestCase

from aworker.task import Worker
from aworker.queue.memory import MemoryQueue
from aworker.serializers import PickleSerializer


def x2(x):
    return x * 2

async def async_x2(x):
    return x * 2


class WorkerTestCase(TestCase):
    def test_register(self):
        mq = MemoryQueue(config=dict(queue=queue.Queue()))
        worker = Worker(mq)

        x2_task = worker.register('x2')(x2)
        self.assertEqual(x2_task.task_name, 'x2')

        ax2_task = worker.register('ax2')(async_x2)
        self.assertEqual(ax2_task.task_name, 'ax2')

    def test_memory_queue(self):
        queue_instance = queue.Queue()
        mq = MemoryQueue(config=dict(queue=queue_instance))
        worker = Worker(mq)

        x2_task = worker.register('x2')(x2)
        ax2_task = worker.register('ax2')(async_x2)

        task_info1 = x2_task.later(4)
        task_info_queue1 = queue_instance.get()
        self.assertEqual(task_info1, task_info_queue1)

        task_info2 = ax2_task.later(3)
        task_info_queue2 = queue_instance.get()
        self.assertEqual(task_info2, task_info_queue2)

    def test_pickled_memory_queue(self):
        queue_instance = queue.Queue()
        mq = MemoryQueue(config=dict(queue=queue_instance), serializer=PickleSerializer())
        worker = Worker(mq)

        x2_task = worker.register('x2')(x2)
        task_info = x2_task.later(4)

        ps = PickleSerializer()
        task_info_queue = queue_instance.get()
        self.assertEqual(ps.unpack(task_info_queue), task_info)


