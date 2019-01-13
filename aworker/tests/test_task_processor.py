import queue
from unittest import TestCase

from aworker.queue.memory import MemoryQueue
from aworker.task import Worker
from aworker.processor import start_worker, WorkProcessor

async def ax2(x):
    return x * 2


def exit_signal_task(wp):
    wp.request_shutdown = True


class WorkProcessorTestCase(TestCase):
    def setUp(self):
        self.queue_instance = queue.Queue()
        self.mq = MemoryQueue(config=dict(queue=self.queue_instance))
        self.worker = Worker(self.mq)

    def test_run(self):
        x2_func = self.worker.register('ax2')(ax2)
        later_task_info = x2_func.later(5)
        self.assertEqual(later_task_info.task_name, 'ax2')
        exit_func = self.worker.register('exit')(exit_signal_task)

        wp = WorkProcessor(self.worker, debug=True)
        exit_func.later(wp)
        wp.run()
