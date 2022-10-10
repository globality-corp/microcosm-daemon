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
        self.heartbeat_timeout = graph.config.health_reporter.heartbeat_timeout

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

            logger.exception(
                "Caught error during state evaluation",
                extra=dict(error=error),
            )

    def heartbeat(self):
        if requests is None:
            return

        try:
            requests.post(
                f"{self.healthcheck_server_host}:{self.healthcheck_server_port}/api/heartbeat",
                json={"pid": os.getpid()},
                timeout=self.heartbeat_timeout,
            )
        except Exception as err:
            logger.debug("Failed to send heartbeat", extra=dict(error=err))  # noqa: G200


@defaults(
    healthcheck_server_host="http://localhost",
    healthcheck_server_port=typed(int, default_value=80),
    heartbeat_timeout=typed(int, 1),
)
def configure_health_reporter(graph):
    return HealthReporter(graph)
