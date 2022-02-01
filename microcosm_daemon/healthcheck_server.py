from logging import getLogger
from time import time
from typing import Dict

import bjoern
from flask import Flask, jsonify, request


def now():
    return int(time())


def create_app(processes: int, heartbeat_threshold_seconds: int):
    healthcheck_app = Flask(__name__)
    heartbeats: Dict[str, int] = dict()

    @healthcheck_app.route("/api/v1/health")
    def healthcheck():
        if not heartbeats:
            return {}, 500

        ts = now()
        last_heartbeats = {
            str(pid): ts - last_ts
            for pid, last_ts in heartbeats.items()
        }
        status = (
            200
            if (
                max(last_heartbeats.values()) <= heartbeat_threshold_seconds and
                len(last_heartbeats) == processes
            )
            else 500
        )

        return jsonify(
            heartbeats=last_heartbeats,
        ), status

    @healthcheck_app.route("/api/v1/heartbeat", methods=["POST"])
    def worker_status():
        logger = getLogger("healthcheck_server")
        req_data = request.get_json()
        pid = int(req_data.get("pid"))

        if not pid:
            return {}, 400
        else:
            logger.debug(f"Received heartbeat from {pid}")
            heartbeats[pid] = now()
            return {}, 201

    return healthcheck_app


def run(
    processes: int,
    heartbeat_threshold_seconds: int,
    healthcheck_host: str,
    healthcheck_port: int,
    **kwargs,
):
    bjoern.run(
        create_app(processes, heartbeat_threshold_seconds),
        healthcheck_host,
        healthcheck_port,
    )
