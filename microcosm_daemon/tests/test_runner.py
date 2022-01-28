import os
from multiprocessing import Pool
from signal import SIGINT, SIGTERM
from threading import Thread
from time import sleep
from unittest.mock import Mock, patch

from parameterized import parameterized

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
    runner = ProcessRunner(2, daemon)
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
