import queue
import time

from aworker.queue.base import BaseQueue, RawTask
from aworker.serializers import BaseSerializer


class IdentitySerializer(BaseSerializer):
    def pack(self, task_info, string_encoded=False):
        return task_info

    def unpack(self, value):
        return value


class MemoryQueue(BaseQueue):
    default_serializer_class = IdentitySerializer

    def __init__(self, config=None, serializer=None):
        super(MemoryQueue, self).__init__(config=config, serializer=serializer)
        self.memory_queue = self.config.get('queue', queue.Queue())

    def send_task(self, task_info):
        self.memory_queue.put(self.serializer.pack(task_info))

    def task_receiver(self, output_queue):
        while not self.exit_receiver:
            try:
                packed_task = self.memory_queue.get(block=True, timeout=1)
                task = self.serializer.unpack(packed_task)
                output_queue.put(RawTask(task, task))
            except queue.Empty:
                time.sleep(.5)
            except Exception as e:
                print(e)
                time.sleep(5)

    async def task_ack(self, raw_task):
        pass
