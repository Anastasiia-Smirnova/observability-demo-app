# Observability Demo App

A small Flask app for the Azure monitoring lab. It sends requests, logs, exceptions and one custom span to Application Insights.

## Endpoints

| Route | Behaviour |
| --- | --- |
| `GET /` | "App is running", HTTP 200 |
| `GET /slow` | Waits 2–6 s (custom span `slow-work`, attribute `demo.delay_seconds`), HTTP 200 |
| `GET /error` | Logs the stack trace and raises an unhandled exception, HTTP 500 |
| `GET /health` | `{"status": "ok"}`, HTTP 200 |
| anything else | Flask default 404 |

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py                      # http://localhost:8000
```

Telemetry is only sent when `APPLICATIONINSIGHTS_CONNECTION_STRING` is set. To test it locally:

```bash
export APPLICATIONINSIGHTS_CONNECTION_STRING="<connection string>"   # PowerShell: $env:APPLICATIONINSIGHTS_CONNECTION_STRING="..."
python app.py
```

## Deploy to Azure App Service

From the folder with `app.py` (Azure CLI or Cloud Shell):

```bash
az webapp up --name app-obsdemo-<yourname> --resource-group rg-monitoring-lab \
  --location swedencentral --runtime PYTHON:3.12 --sku F1 --logs
```

No startup command is needed: App Service finds `app.py` with the `app` object and runs it with gunicorn.

Then set the connection string (Application Insights → Overview → Connection String):

```bash
az webapp config appsettings set --name app-obsdemo-<yourname> --resource-group rg-monitoring-lab \
  --settings APPLICATIONINSIGHTS_CONNECTION_STRING="<connection string>"
```

Redeploy after code changes with `az webapp up` in the same folder.

## Notes

- `configure_azure_monitor()` runs before `from flask import Flask`; otherwise Flask requests are not tracked.
- `logger_name="obsdemo"` sends only this app's log lines to Application Insights, not library noise.
- The custom span appears in the `dependencies` table (`name == "slow-work"`).
