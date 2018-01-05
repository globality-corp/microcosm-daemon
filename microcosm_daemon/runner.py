"""
Execution abstraction.

"""
from multiprocessing import Pool


class SimpleRunner:
    """
    Run a daemon in the current process.

    """

    def __init__(self, target, *args, **kwargs):
        self.target = target
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.target.start(*self.args, **self.kwargs)


def _start(target, *args, **kwargs):
    target.start(*args, **kwargs)


class ProcessRunner:
    """
    Run a daemon in a different process.

    """

    def __init__(self, processes, target, *args, **kwargs):
        self.processes = processes
        self.target = target
        self.args = args
        self.kwargs = kwargs

    def run(self):
        pool = Pool(processes=self.processes)
        for _ in range(self.processes):
            pool.apply_async(_start, (self.target,) + self.args, self.kwargs)

        pool.close()
        try:
            pool.join()
        except KeyboardInterrupt:
            pool.join()
