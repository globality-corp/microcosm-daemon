"""
Sleep policy tests.

"""
from hamcrest import (
    assert_that,
    equal_to,
    is_,
)
from mock import patch

from microcosm_daemon.sleep_policy import SleepPolicy, SleepNow


def test_no_sleep():
    """
    Do not sleep if SleepNow is not raised.

    """
    sleep_policy = SleepPolicy(default_sleep_timeout=0.1)

    with patch.object(sleep_policy, "sleep") as mocked_sleep:
        pass

    assert_that(mocked_sleep.call_count, is_(equal_to(0)))


def test_sleep_now():
    """
    Sleep if SleepNow is raised.

    """
    sleep_policy = SleepPolicy(default_sleep_timeout=0.1)

    with patch.object(sleep_policy, "sleep") as mocked_sleep:
        with sleep_policy:
            raise SleepNow()

    assert_that(mocked_sleep.call_count, is_(equal_to(1)))
    mocked_sleep.assert_called_with(0.1)


def test_sleep_now_custom_timeout():
    """
    Sleep custom amount if SleepNow is raised with a timeout.

    """
    sleep_policy = SleepPolicy(default_sleep_timeout=0.1)

    with patch.object(sleep_policy, "sleep") as mocked_sleep:
        with sleep_policy:
            raise SleepNow(0.2)

    assert_that(mocked_sleep.call_count, is_(equal_to(1)))
    mocked_sleep.assert_called_with(0.2)
