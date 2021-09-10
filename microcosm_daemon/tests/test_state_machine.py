"""
State machine tests.

"""
from unittest.mock import patch

from hamcrest import (
    assert_that,
    calling,
    equal_to,
    is_,
    raises,
)
from microcosm.api import create_object_graph

from microcosm_daemon.error_policy import FatalError
from microcosm_daemon.sleep_policy import SleepNow
from microcosm_daemon.state_machine import StateMachine


def test_step_to_same_func():
    """
    Test taking a step to the same function.

    """
    graph = create_object_graph("example", testing=True)

    def func(graph):
        pass

    state_machine = StateMachine(graph, initial_state=func)
    next_func = state_machine.step()
    assert_that(next_func, is_(equal_to(func)))


def test_step_to_different_func():
    """
    Test taking a step to a different function.

    """
    graph = create_object_graph("example", testing=True)

    def func1(graph):
        return func2

    def func2(graph):
        pass

    state_machine = StateMachine(graph, initial_state=func1)
    next_func = state_machine.step()
    assert_that(next_func, is_(equal_to(func2)))


def test_step_to_sleep():
    """
    Test taking a step to sleep.

    """
    graph = create_object_graph("example", testing=True)

    def func(graph):
        raise SleepNow()

    state_machine = StateMachine(graph, initial_state=func)
    with patch.object(graph.sleep_policy, "sleep") as mocked_sleep:
        next_func = state_machine.step()

    assert_that(mocked_sleep.call_count, is_(equal_to(1)))
    assert_that(next_func, is_(equal_to(func)))


def test_step_to_error_non_strict():
    """
    Test taking a step to an error.

    """
    graph = create_object_graph("example", testing=True)

    def func(graph):
        raise Exception()

    state_machine = StateMachine(graph, initial_state=func)
    assert_that(graph.error_policy.strict, is_(equal_to(False)))

    next_func = state_machine.step()
    assert_that(next_func, is_(equal_to(func)))


def test_step_to_fatal_non_strict():
    """
    Test taking a step to an error.

    """
    graph = create_object_graph("example", testing=True)

    def func(graph):
        raise FatalError()

    state_machine = StateMachine(graph, initial_state=func)
    assert_that(graph.error_policy.strict, is_(equal_to(False)))

    assert_that(calling(state_machine.step), raises(FatalError))


def test_run_until_fatal_error():
    """
    Running the state machine terminates on fatal error.

    """
    graph = create_object_graph("example", testing=True)

    def func(graph):
        raise FatalError()

    state_machine = StateMachine(graph, initial_state=func)
    state_machine.run()
