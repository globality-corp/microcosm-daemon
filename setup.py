#!/usr/bin/env python
from setuptools import find_packages, setup

project = "microcosm-daemon"
version = "1.5.0"

setup(
    name=project,
    version=version,
    description="Asynchronous workers",
    author="Globality Engineering",
    author_email="engineering@globality.com",
    url="https://github.com/globality-corp/microcosm-daemon",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    python_requires=">=3.6",
    zip_safe=False,
    install_requires=[
        "microcosm>=2.12.0",
        "microcosm-logging>=1.0.0",
    ],
    setup_requires=[
        "nose>=1.3.6",
    ],
    dependency_links=[
    ],
    entry_points={
        "microcosm.factories": [
            "error_policy = microcosm_daemon.error_policy:configure_error_policy",
            "health_reporter = microcosm_daemon.health_reporter:configure_health_reporter",
            "signal_handler = microcosm_daemon.signal_handler:configure_signal_handler",
            "sleep_policy = microcosm_daemon.sleep_policy:configure_sleep_policy",
        ]
    },
    extras_require={
        "test": [
            "coverage>=3.7.1",
            "parameterized>=0.8.1",
            "PyHamcrest>=1.8.5",
        ],
        "healthcheck": [
            "waitress>=2.0.0",
            "Flask<2",
            "Flask>=1.0.2",
            # Due to https://github.com/pallets/jinja/issues/1585
            "markupsafe<2.1",
            "requests>=2.27.1",
        ],
    },
    tests_require=[
        "coverage>=3.7.1",
        "parameterized>=0.8.1",
        "PyHamcrest>=1.8.5",
    ],
)
