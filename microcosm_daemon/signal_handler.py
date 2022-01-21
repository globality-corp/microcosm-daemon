"""
Signal handling.

"""
from os import getpid
from signal import SIGINT, SIGTERM, signal


class SignalHandler:
    """
    Handle signals raised during state machine execution.

    """

    def __init__(self, graph):
        self.logger = graph.logger

        self.signalnums = [SIGINT, SIGTERM]
        self.interrupted = False

    def __call__(self, signalnum, frame):
        self.logger.info(f"Signal {signalnum} received, PID: {getpid()}")

        self.interrupted = True

    def __enter__(self):
        for signalnum in self.signalnums:
            signal(signalnum, self)

    def __exit__(self, type, value, traceback):
        pass


def configure_signal_handler(graph):
    return SignalHandler(graph)
