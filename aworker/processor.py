import asyncio


class WorkProcessor(object):
    def __init__(self, worker):
        self.worker = worker

    def double_function(self, t):
        print("Doubling {}".format(t))
        return t * 2

    async def run(self):
        print("Running...")
        await asyncio.sleep(self.double_function(3))
        print("Exiting...")


def start_worker(worker):
    wp = WorkProcessor(worker)
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    loop.run_until_complete(wp.run())

if __name__ == '__main__':
    start_worker(None)
