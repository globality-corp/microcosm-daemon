"""
Test daemon loading.

"""
from unittest.mock import Mock, patch

from hamcrest import assert_that, equal_to, is_
from requests import get

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



# def test_healtcheck_server():
#     daemon = FixtureDaemon()

#     with patch.object(daemon, "make_arg_parser") as mock_args_parser:
#         mock_args_parser.return_value = Mock(
#             parse_args=Mock(
#                 return_value=Mock(
#                     processes=2,
#                     heartbeat_threshold_seconds=10,
#                     healthcheck_host="0.0.0.0",
#                     healthcheck_port=80,
#                 ),
#             ),
#         )
#         daemon.run()
#     resp = get("http://localhost:80/api/v1/health")
#     assert_that(
#         resp.status_code,
#         equal_to(200),
#     )