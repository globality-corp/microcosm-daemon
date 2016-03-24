"""
Expose core state machine and errors.

"""
from microcosm_daemon.error_policy import FatalError
from microcosm_daemon.sleep_policy import SleepNow
from microcosm_daemon.state_machine import StateMachine


__all__ = [
    FatalError,
    SleepNow,
    StateMachine
]
