"""
Standby state machine.

"""
from abc import ABCMeta, abstractproperty
from six import add_metaclass

from microcosm_daemon.sleep_policy import SleepNow


class StandByGuard(object):
    """
    State wrapper for a standby-enabled daemon.

    Calls state and then checks condition.

    """
    def __init__(self, next_state, condition):
        self.next_state = next_state
        self.condition = condition

    def __str__(self):
        return str(self.next_state)

    def __call__(self, graph):
        """
        Invoke the wrapped state and then check the standby condition.

        """
        result = self.next_state(graph)

        should_standby = self.condition(graph)
        if should_standby:
            return StandByState(result or self.next_state, self.condition)

        return StandByGuard(result, self.condition)


class StandByState(object):
    """
    State for a daemon that is in standby.

    Remains in standby until condition is met.

    """
    def __init__(self, next_state, condition):
        self.next_state = next_state
        self.condition = condition

    def __str__(self):
        return "standby"

    def __call__(self, graph):
        """
        Check the standby condition before advancing to the next state.

        """
        should_standby = self.condition(graph)
        if should_standby:
            raise SleepNow(None)

        return StandByGuard(self.next_state, self.condition)


@add_metaclass(ABCMeta)
class StandByMixin(object):
    """
    Mixin for a daemon to inject standby logic.

    """
    @abstractproperty
    def standby_condition(self):
        """
        Define a stand by condition.

        Should return a function that takes a graph and returns boolean.

        """
        pass

    @property
    def initial_state(self):
        return StandByState(self, self.standby_condition)
