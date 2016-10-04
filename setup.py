#!/usr/bin/env python
from setuptools import find_packages, setup

project = "microcosm_daemon"
version = "0.8.0"

setup(
    name=project,
    version=version,
    description="Asynchronous workers",
    author="Globality Engineering",
    author_email="engineering@globality.com",
    url="https://github.com/globality-corp/microcosm-daemon",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "microcosm>=0.7.0",
        "microcosm-logging>=0.3.0",
    ],
    setup_requires=[
        "nose>=1.3.6",
    ],
    dependency_links=[
    ],
    entry_points={
        "microcosm.factories": [
            "error_policy = microcosm_daemon.error_policy:configure_error_policy",
            "signal_handler = microcosm_daemon.signal_handler:configure_signal_handler",
            "sleep_policy = microcosm_daemon.sleep_policy:configure_sleep_policy",
        ]
    },
    tests_require=[
        "coverage>=3.7.1",
        "mock>=1.0.1",
        "PyHamcrest>=1.8.5",
    ],
)
