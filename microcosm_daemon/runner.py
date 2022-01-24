"""
Execution abstraction.

"""
from multiprocessing import Pool
from signal import SIGINT, SIGTERM, signal


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

    def __init__(self, target, processes, *args, **kwargs):
        self.processes = processes
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.pool = None
        self.healthcheck_server = None

        self.init_signal_handlers()
        self.init_healthcheck_server()

    def run(self):
        self.pool = Pool(processes=self.processes)

        for _ in range(self.processes):
            self.pool.apply_async(_start, (self.target,) + self.args, self.kwargs)

        if self.healthcheck_server:
            self.healthcheck_server(**self.kwargs)
        else:
            self.close()

    def init_signal_handlers(self):
        for signum in (SIGINT, SIGTERM):
            signal(signum, self.on_terminate)

    def init_healthcheck_server(self):
        try:
            from microcosm_daemon.healthcheck_server import run

            self.healthcheck_server = run
        except ImportError:
            self.healthcheck_server = None

    def close(self, terminate=False):
        if self.pool is not None:
            if terminate:
                self.pool.terminate()
            else:
                self.pool.close()

            try:
                self.pool.join()
            except KeyboardInterrupt:
                self.pool.join()

        exit(0)

    def on_terminate(self, signum, frame):
        self.close(terminate=True)
