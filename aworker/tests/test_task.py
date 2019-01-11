import asyncio
from unittest import TestCase

from aworker.task import Task


def simple_doubler(n):
    return n*2

async def async_doubler(n):
    return n*2


class TaskTestCase(TestCase):
    def setUp(self):
        pass

    def test_simple_task(self):
        t = Task(simple_doubler, None, None)

        self.assertFalse(t.is_async())

        self.assertEqual(t(4), 8)

    def test_async_task(self):
        t = Task(async_doubler, None, None)

        self.assertTrue(t.is_async())
        self.assertEqual(t(4), 8)

        loop = asyncio.get_event_loop()
        loop.set_debug(True)
        result = loop.run_until_complete(t.run_async(3))
        self.assertEqual(result, 6)
