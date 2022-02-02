import os
from logging import DEBUG
from multiprocessing import Pool
from signal import SIGINT, SIGTERM
from threading import Thread
from time import sleep
from unittest.mock import Mock, patch

from hamcrest import assert_that, equal_to
from parameterized import parameterized
from requests import get

from microcosm_daemon.api import SleepNow
from microcosm_daemon.daemon import Daemon
from microcosm_daemon.runner import ProcessRunner


class FixtureDaemon(Daemon):

    @property
    def name(self):
        return "fixture"

    def __call__(self, *args, **kwargs):
        raise SleepNow()


def sleep_and_send_signal(pid, seconds, signum):
    def exec():
        sleep(seconds)
        os.kill(pid, signum)

    return exec


@parameterized([
    (SIGINT,),
    (SIGTERM,),
])
def test_process_runner_to_terminate_pool(signum):
    daemon = FixtureDaemon()
    pool = Mock(wraps=Pool(2))
    runner = ProcessRunner(
        daemon,
        2,
        heartbeat_threshold_seconds=-1,
        healthcheck_host="0.0.0.0",
        healthcheck_port=80,
    )
    terminated = False

    with patch.object(runner, "process_pool") as mocked_process_pool:
        mocked_process_pool.return_value = pool

        # starting thread, meant to send signal in 2 seconds
        thread = Thread(
            target=sleep_and_send_signal(
                pid=os.getpid(),
                seconds=2,
                signum=signum,
            ),
        )
        thread.daemon = True
        thread.start()

        try:
            runner.run()
        except SystemExit:
            terminated = True

    assert terminated

    pool.close.assert_called_once()
    pool.terminate.assert_called_once()

def sleep_check_health_and_send_signal(pid, seconds, signum):
    def exec():
        sleep(seconds)

        # resp = get("http://localhost:80/api/v1/health")

        os.kill(pid, signum)
        # assert_that(
        #     resp.status_code,
        #     equal_to(200),
        # )

    return exec

def test_healtcheck_server():
    daemon = FixtureDaemon()

    # starting thread, meant to send signal in 2 seconds
    thread = Thread(
        target=sleep_check_health_and_send_signal(
            pid=os.getpid(),
            seconds=2,
            signum=SIGTERM,
        ),
    )
    thread.daemon = True
    try:
        thread.start()
    except AssertionError:
        raise False

    with patch.object(daemon, "make_arg_parser") as mock_args_parser:
        mock_args_parser.return_value = Mock(
            parse_args=Mock(
                return_value=Mock(
                    processes=2,
                    heartbeat_threshold_seconds=10,
                    healthcheck_host="0.0.0.0",
                    healthcheck_port=80,
                ),
            ),
        )
        try:
            daemon.run()
        except SystemExit:
            print("TERMINATED")
            terminated = True

    assert terminated
