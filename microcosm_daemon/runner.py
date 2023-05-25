"""
Execution abstraction.

"""
from logging import getLogger
from multiprocessing import Pool
from signal import SIGINT, SIGTERM, signal


logger = getLogger("daemon.process_runner")


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
        self.init_healthcheck_server(**kwargs)

    def run(self):
        self.pool = self.process_pool()

        for _ in range(self.processes):
            self.pool.apply_async(_start, (self.target,) + self.args, self.kwargs, error_callback=self.on_error)

        if self.healthcheck_server:
            self.healthcheck_server(self.processes, **self.kwargs)
            # The healthcheck server will block while running, and swallow any SystemExit exception
            # If we're reaching this point, we're exiting and need to re-raise `SystemExit`
            exit(0)
        else:
            self.close()

    def init_signal_handlers(self):
        for signum in (SIGINT, SIGTERM):
            signal(signum, self.on_terminate)

    def init_healthcheck_server(self, heartbeat_threshold_seconds: int = -1, **kwargs):
        if heartbeat_threshold_seconds < 0:
            self.healthcheck_server = None
            return

        from microcosm_daemon.healthcheck_server import run
        self.healthcheck_server = run

    def process_pool(self):
        return Pool(processes=self.processes)

    def close(self, terminate=False):
        if self.pool is not None:
            if terminate:
                self.pool.terminate()
            else:
                self.pool.close()

            self.pool.join()

        exit(0)

    def on_error(self, error):
        logger.error("Error while running async processor: %s", error)
        self.close(terminate=True)

    def on_terminate(self, signum, frame):
        self.close(terminate=True)
