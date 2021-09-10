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

from microcosm_daemon.error_policy import ErrorPolicy, FatalError


def test_no_error_strict():
    """
    Error handling is a noop if there are no errors.

    """
    error_policy = ErrorPolicy(strict=True, health_report_interval=3.0)
    with error_policy:
        pass

    assert_that(error_policy.errors, is_(equal_to([])))


def test_no_error_non_strict():
    """
    Error handling is a noop if there are no errors.

    """
    error_policy = ErrorPolicy(strict=False, health_report_interval=3.0)
    with error_policy:
        pass

    assert_that(error_policy.errors, is_(equal_to([])))


def test_error_non_strict():
    """
    Non strict error handling captures errors.

    """
    error_policy = ErrorPolicy(strict=False, health_report_interval=3.0)
    error = Exception()

    with error_policy:
        raise error

    assert_that(error_policy.errors, contains(error))


def test_error_strict():
    """
    Strict error handling raises errors.

    """
    error_policy = ErrorPolicy(strict=True, health_report_interval=3.0)
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
    error_policy = ErrorPolicy(strict=False, health_report_interval=3.0)
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
    error_policy = ErrorPolicy(strict=True, health_report_interval=3.0)
    error = FatalError()

    def defer():
        with error_policy:
            raise error

    assert_that(calling(defer), raises(FatalError))
    assert_that(error_policy.errors, contains(error))
