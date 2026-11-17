import logging
import random
import time

import newrelic.agent
newrelic.agent.initialize()   # reads NEW_RELIC_* environment variables; must run before Flask is imported

from flask import Flask, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("obsdemo")
logger.setLevel(logging.INFO)

app = Flask(__name__)

@app.route("/")
def index():
    logger.info("route=/")
    return "App is running\n"

@app.route("/slow")
def slow():
    delay = random.uniform(2, 6)
    newrelic.agent.add_custom_attribute("demo.delay_seconds", round(delay, 2))
    with newrelic.agent.FunctionTrace(name="slow-work"):
        time.sleep(delay)
    logger.info("route=/slow delay=%.2fs", delay)
    return f"Done after {delay:.2f} seconds\n"

@app.route("/error")
def error():
    logger.info("route=/error")
    try:
        raise RuntimeError("Intentional test error from /error")
    except RuntimeError:
        logger.exception("Unhandled exception in /error")
        raise


@app.route("/health")
def health():
    logger.info("route=/health")
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
