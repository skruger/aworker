import asyncio
import uuid

from aworker.serializers import TaskInfo
from aworker.exceptions import DuplicateTaskError


class Task(object):
    def __init__(self, fn, task_name, worker, **options):
        self.fn = fn
        self.task_name = task_name
        self.worker = worker
        self.options = options

    def is_async(self):
        return asyncio.iscoroutinefunction(self.fn)

    async def run_async(self, *args, **kwargs):
        return await self.fn(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.is_async():
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.run_async(*args, **kwargs))

        return self.fn(*args, **kwargs)

    def later(self, *args, **kwargs):
        task_info = TaskInfo(self.task_name, args, kwargs, dict())
        self.worker.queue.send_task(task_info)
        return task_info


class Worker(object):
    def __init__(self, queue, **config):
        self.queue = queue
        self.config = config
        self.tasks = dict()

    def register(self, name, **options):
        def wrapper(fn):
            t = Task(fn, name, self, **options)
            if name in self.tasks:
                raise DuplicateTaskError("Task named '{}' already registered.".format(name))
            self.tasks[name] = t

            return t

        return wrapper

    def get_task(self, task_info):
        return self.tasks.get(task_info.task_name)

    def send_queue(self, task, args, kwargs, options):
        pass
