# AWorker

Task queue worker that can process functions written in regular python and asyncio coroutines.

## Configuration

In order to configure your task worker create
a queue driver and pass it in when creating
your `Worker`.

### Queue driver
Each queue type requires a queue driver. If you
want to use an unsupported queue type you can 
create a new class based on BaseQueue and implement
the required methods.

### Worker
The worker class is used to register tasks and
call tasks based on messages found on the queue. 

```python
import asyncio
import time
from queue import Queue
from aworker.task import Worker
from aworker.queue.memory import MemoryQueue

queue_driver = MemoryQueue(config=dict(queue=Queue()))
worker = Worker(queue=queue_driver)

# These usually go in a different file
@worker.register('async_sleep_and_muliply2')
async def sleep_and_multiply2(x):
    await asyncio.sleep(x)
    return x * 2

@worker.register('sync_sleep_and_muliply2')
def sync_sleep_and_multiply2(x):
    time.sleep(x)
    return x * 2

# Send to the task queue be executed later
sleep_and_multiply2.later(3)
sync_sleep_and_multiply2.later(2)
```

## Running the Work Processor

```bash
aworker run 'myproject.tasks:worker'
```
