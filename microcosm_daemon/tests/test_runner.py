import os
from multiprocessing import Pool
from signal import SIGINT, SIGTERM
from subprocess import Popen
from threading import Thread
from time import sleep
from unittest.mock import Mock, patch

from hamcrest import assert_that, equal_to, has_length
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


if __name__ == "__main__":
    daemon = FixtureDaemon()
    daemon.run()


@parameterized(
    (1,),
    (2,),
)
def test_healtcheck_server(num_processes):
    popen_instance = Popen(
        f"python microcosm_daemon/tests/test_runner.py --processes {num_processes} --heartbeat-threshold-seconds 2",
        shell=True,
    )
    sleep(2)
    resp = get("http://localhost:80/api/health")
    assert_that(resp.status_code, equal_to(200))
    assert_that(resp.json()["heartbeats"], has_length(2))
    popen_instance.terminate()
