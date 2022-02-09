"""
Test daemon loading.

"""

from hamcrest import assert_that, equal_to, is_

from microcosm_daemon.daemon import Daemon


class FixtureDaemon(Daemon):

    @property
    def name(self):
        return "fixture"

    @property
    def components(self):
        return super(FixtureDaemon, self).components + [
            "hello_world",
        ]

    def __call__(self):
        pass


def test_daemon_initialize():
    daemon = FixtureDaemon.create_for_testing()
    assert_that(daemon.graph.hello_world, is_(equal_to("hello world")))
    assert_that(daemon.name, is_(equal_to("fixture")))
    assert_that(str(daemon), is_(equal_to("fixture_daemon")))
