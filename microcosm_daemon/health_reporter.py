import os
from logging import getLogger

from microcosm.api import defaults, typed

from microcosm_daemon.error_policy import ExitError


try:
    import requests
except ImportError:
    requests = None  # type:ignore


logger = getLogger("daemon.health_reporter")


class HealthReporter:
    def __init__(self, graph):
        self.healthcheck_server_host = graph.config.health_reporter.healthcheck_server_host
        self.healthcheck_server_port = graph.config.health_reporter.healthcheck_server_port

    def __call__(self, health, prev_health, errors):
        self.heartbeat()

        message = f"Health is {health}"

        if prev_health != health:
            logger.info(message)
        else:
            logger.debug(message)

        for error in errors:
            if isinstance(error, ExitError):
                continue

            logger.warn(f"Caught error during state evaluation: {error}", exc_info=True)

    def heartbeat(self):
        if requests is None:
            return

        try:
            requests.post(
                f"{self.healthcheck_server_host}:{self.healthcheck_server_port}/api/v1/heartbeat",
                json={"pid": os.getpid()},
            )
        except Exception as err:
            logger.debug(f"Failed to send heartbeat: {err}")


@defaults(
    healthcheck_server_host="http://localhost",
    healthcheck_server_port=typed(bool, default_value=80),
)
def configure_health_reporter(graph):
    return HealthReporter(graph)
