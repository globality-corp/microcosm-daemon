"""
Standby state tests.

"""
from hamcrest import assert_that, equal_to, is_, instance_of
from mock import MagicMock

from microcosm.api import create_object_graph
from microcosm_daemon.daemon import Daemon
from microcosm_daemon.standby import StandByGuard, StandByMixin, StandByState
from microcosm_daemon.state_machine import StateMachine


def make_alternating_condition():
    """
    Create a function that simulates a standby condition that alternates.

    """
    condition = MagicMock()
    condition.side_effect = [
        True,
        False,
        True,
        False,
    ]
    return condition


def example_non_standby_state(graph):
    """
    Example of a non-standby state.

    """
    pass


class StandByDaemon(StandByMixin, Daemon):
    """
    Example of a daemon that supports standby.

    """
    @property
    def name(self):
        return "test"

    @property
    def standby_condition(self):
        return make_alternating_condition()

    def __call__(self, graph):
        pass


def assert_that_states_alternate(state_machine, non_standby_state):
    """
    Assert that a state machine alternates states.

    """
    next_state = state_machine.advance()
    assert_that(next_state, is_(instance_of(StandByState)))
    assert_that(next_state.next_state, is_(equal_to(non_standby_state)))

    next_state = state_machine.advance()
    assert_that(next_state, is_(instance_of(StandByGuard)))
    assert_that(next_state.next_state, is_(equal_to(non_standby_state)))

    next_state = state_machine.advance()
    assert_that(next_state, is_(instance_of(StandByState)))
    assert_that(next_state.next_state, is_(equal_to(non_standby_state)))

    next_state = state_machine.advance()
    assert_that(next_state, is_(instance_of(StandByGuard)))
    assert_that(next_state.next_state, is_(equal_to(non_standby_state)))


def test_standby():
    """
    StandBy state with alternating condition should alternate.

    """
    graph = create_object_graph("test", testing=True)
    initial_state = StandByState(example_non_standby_state, make_alternating_condition())
    state_machine = StateMachine(graph, initial_state, never_reload=True)
    assert_that_states_alternate(state_machine, example_non_standby_state)


def test_standby_mixin():
    """
    Daemon that uses `StandByMixin` should alternate.

    """
    daemon = StandByDaemon.create_for_testing()
    state_machine = StateMachine(daemon.graph, daemon.initial_state)
    assert_that_states_alternate(state_machine, daemon)
