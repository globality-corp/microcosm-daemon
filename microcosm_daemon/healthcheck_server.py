from time import time

import bjoern
from flask import Flask, jsonify, request


def now():
    return int(time())


def create_app():
    healthcheck_app = Flask(__name__)
    heartbeats = dict()
    # TODO accept as config params
    max_heartbeat_seconds = 5
    processes = 4

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
                max(last_heartbeats.values()) <= max_heartbeat_seconds and
                len(last_heartbeats) == processes
            )
            else 500
        )

        return jsonify(
            heartbeats=last_heartbeats,
        ), status

    @healthcheck_app.route("/api/v1/heartbeat", methods=["POST"])
    def worker_status():
        req_data = request.get_json()
        pid = int(req_data.get("pid"))

        if not pid:
            return {}, 400
        else:
            heartbeats[pid] = now()
            return {}, 201

    return healthcheck_app


def run(healthcheck_host, healthcheck_port, **kwargs):

    bjoern.run(create_app(), healthcheck_host, healthcheck_port)
