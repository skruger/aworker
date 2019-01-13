import queue
from unittest import TestCase

from aworker.task import Worker
from aworker.queue.memory import MemoryQueue
from aworker.serializers import PickleSerializer
from aworker.exceptions import DuplicateTaskError


def x2(x):
    return x * 2

async def async_x2(x):
    return x * 2


class WorkerTestCase(TestCase):
    def setUp(self):
        self.queue_instance = queue.Queue()
        self.mq = MemoryQueue(config=dict(queue=self.queue_instance))
        self.worker = Worker(self.mq)

    def test_register(self):
        x2_task = self.worker.register('x2')(x2)
        self.assertEqual(x2_task.task_name, 'x2')
        self.assertIn('x2', self.worker.tasks)

        ax2_task = self.worker.register('ax2')(async_x2)
        self.assertEqual(ax2_task.task_name, 'ax2')
        self.assertIn('ax2', self.worker.tasks)

    def test_register_duplicate(self):
        self.worker.register('x2')(x2)
        with self.assertRaises(DuplicateTaskError):
            self.worker.register('x2')(async_x2)

    def test_memory_queue(self):
        x2_task = self.worker.register('x2')(x2)
        ax2_task = self.worker.register('ax2')(async_x2)

        task_info1 = x2_task.later(4)
        task_info_queue1 = self.queue_instance.get()
        self.assertEqual(task_info1, task_info_queue1)

        task_info2 = ax2_task.later(3)
        task_info_queue2 = self.queue_instance.get()
        self.assertEqual(task_info2, task_info_queue2)

    def test_pickled_memory_queue(self):
        self.worker.queue.serializer=PickleSerializer()

        x2_task = self.worker.register('x2')(x2)
        task_info = x2_task.later(4)

        ps = PickleSerializer()
        task_info_queue = self.queue_instance.get()
        self.assertEqual(ps.unpack(task_info_queue), task_info)
