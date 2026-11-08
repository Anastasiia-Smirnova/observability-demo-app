import logging
import os
import random
import time

# Telemetry must be configured BEFORE Flask is imported, so requests are tracked
if os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    from azure.monitor.opentelemetry import configure_azure_monitor
    configure_azure_monitor(logger_name="obsdemo")

from flask import Flask, jsonify
from opentelemetry import trace

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("obsdemo")
logger.setLevel(logging.INFO)
tracer = trace.get_tracer("obsdemo")
app = Flask(__name__)


@app.route("/")
def index():
    logger.info("route=/")
    return "App is running\n"


@app.route("/slow")
def slow():
    delay = random.uniform(2, 6)
    with tracer.start_as_current_span("slow-work") as span:
        span.set_attribute("demo.delay_seconds", round(delay, 2))
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
