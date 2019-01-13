import asyncio
import queue
import concurrent.futures


class WorkProcessor(object):
    def __init__(self, worker, max_threads=2, debug=False):
        """
        WorkProcessor receives data from the queue and executes async coroutines and passes synchronous python
        to a ThreadPoolExecutor with max_workers=max_threads.

        :param worker: <aworker.task.Worker instance>
        :param max_threads: Number of threads to allocate for synchronous python code
        :param debug: Enable debugging so breakpoints work
        """
        self.worker = worker
        self.loop = asyncio.get_event_loop()
        self.loop.set_debug(debug)
        self.request_shutdown = False
        self.work_pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_threads)
        self.queue_pool = concurrent.futures.ThreadPoolExecutor(max_workers=3)
        self.receive_queue = queue.Queue()

    def run(self):
        return self.loop.run_until_complete(self.async_main())

    def double_function(self, t):
        print("Doubling {}".format(t))
        return t * 2

    def run_queue_task_receiver(self):
        return asyncio.ensure_future(
            self.loop.run_in_executor(self.queue_pool, self.worker.queue.task_receiver, self.receive_queue)
        )

    def _execute_task_thread(self, task, task_info):
        return task(*task_info.args, **task_info.kwargs)

    def sync_get_message(self):
        """
        Watch receive_queue for a task. Returns a tuple of (task, raw_task)

        :return: (task, raw_task) | None
        """
        try:
            print("Trying to get message")
            raw_task = self.receive_queue.get(block=True, timeout=1)
            task = self.worker.get_task(raw_task.task_info)
            return task, raw_task
        except queue.Empty:
            print("No message to get!")
            pass

    async def get_message(self):
        """
        Watch receive_queue for a task. Returns a tuple of (future, taskinfo)

        :return: future
        """

        new_task = await asyncio.ensure_future(
            self.loop.run_in_executor(self.queue_pool, self.sync_get_message)
        )
        if new_task:
            task, raw_task = new_task
            return asyncio.ensure_future(self.handle_message(task, raw_task))

    async def handle_message(self, task, raw_task):
        if task.is_async():
            task_future = task.run_async(*raw_task.task_info.args, **raw_task.task_info.kwargs)
        else:
            task_future = asyncio.ensure_future(
                self.loop.run_in_executor(self.work_pool, self._execute_task_thread, task, raw_task.task_info)
            )
        result = await task_future

        # Ack The message to the queue
        await self.worker.queue.task_ack(raw_task)

        return result

    async def async_main(self):
        running_tasks = dict()
        do_shutdown = False
        task_queue_receiver = self.run_queue_task_receiver()
        running_tasks[task_queue_receiver] = 'task_queue_receiver'
        job_fetch_coroutine = None
        while not do_shutdown:
            if self.request_shutdown:
                self.worker.queue.exit_receiver = True
            if not job_fetch_coroutine and not self.receive_queue.empty():
                job_fetch_coroutine = asyncio.ensure_future(self.get_message())
                running_tasks[job_fetch_coroutine] = 'job_fetch_coroutine'
                print("Created job_fetch_coroutine")

            # wait for coroutines
            done_tasks, _ = await asyncio.wait(running_tasks, return_when=asyncio.FIRST_COMPLETED)
            for t in done_tasks:
                if running_tasks[t] == 'task_queue_receiver':
                    await t
                    self.request_shutdown = True

                elif running_tasks[t] == 'job_fetch_coroutine':
                    new_task = await t
                    if new_task:
                        print("Got new task")
                        running_tasks[new_task] = 'task'
                    print("Clearing job_fetch_coroutine")
                    job_fetch_coroutine = None
                else:
                    result = await t
                    print("got result: {}".format(result))

                del running_tasks[t]

            if self.request_shutdown and not running_tasks:
                do_shutdown = True


def start_worker(worker, **settings):
    wp = WorkProcessor(worker, **settings)
    return wp.run()


if __name__ == '__main__':
    start_worker(None)
