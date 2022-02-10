"""
Error policy tests.

"""
from hamcrest import (
    assert_that,
    calling,
    contains,
    equal_to,
    is_,
    raises,
)
from microcosm.api import create_object_graph

from microcosm_daemon.error_policy import ErrorPolicy, FatalError
from microcosm_daemon.health_reporter import HealthReporter


def new_error_policy(strict=True):
    graph = create_object_graph("example", testing=True)

    return ErrorPolicy(
        strict=strict,
        health_report_interval=3.0,
        health_reporter=HealthReporter(graph),
    )


def test_no_error_strict():
    """
    Error handling is a noop if there are no errors.

    """
    error_policy = new_error_policy(strict=True)
    with error_policy:
        pass

    assert_that(error_policy.errors, is_(equal_to([])))


def test_no_error_non_strict():
    """
    Error handling is a noop if there are no errors.

    """
    error_policy = new_error_policy(strict=False)
    with error_policy:
        pass

    assert_that(error_policy.errors, is_(equal_to([])))


def test_error_non_strict():
    """
    Non strict error handling captures errors.

    """
    error_policy = new_error_policy(strict=False)
    error = Exception()

    with error_policy:
        raise error

    assert_that(error_policy.errors, contains(error))


def test_error_strict():
    """
    Strict error handling raises errors.

    """
    error_policy = new_error_policy(strict=True)
    error = Exception()

    def defer():
        with error_policy:
            raise error

    assert_that(calling(defer), raises(Exception))
    assert_that(error_policy.errors, contains(error))


def test_fatal_non_strict():
    """
    Error handling does not capture fatal errors.

    """
    error_policy = new_error_policy(strict=False)
    error = FatalError()

    def defer():
        with error_policy:
            raise error

    assert_that(calling(defer), raises(FatalError))
    assert_that(error_policy.errors, contains(error))


def test_fatal_strict():
    """
    Error handling does not capture fatal errors.

    """
    error_policy = new_error_policy(strict=True)
    error = FatalError()

    def defer():
        with error_policy:
            raise error

    assert_that(calling(defer), raises(FatalError))
    assert_that(error_policy.errors, contains(error))
