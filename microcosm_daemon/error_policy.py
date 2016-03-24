"""
Error handling policy.

"""
from microcosm.api import defaults


class FatalError(Exception):
    """
    Unconditionally exit the state machine.

    """
    pass


class ErrorPolicy(object):
    """
    Handle errors from state functions.

    """
    def __init__(self, strict):
        self.strict = strict
        self.errors = []

    @property
    def healthy(self):
        return not self.errors

    def __enter__(self):
        self.errors = []
        return self

    def __exit__(self, type, value, traceback):
        if value:
            self.errors.append(value)
        return not self.strict and type is not FatalError


@defaults(
    strict=False,
)
def configure_error_policy(graph):
    return ErrorPolicy(
        strict=graph.config.error_policy.strict
    )
