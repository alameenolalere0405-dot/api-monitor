# Pulse — API Monitor

Pulse is a lightweight, responsive dashboard for manually checking public APIs and websites. It is built with Python, Flask, SQLite, and vanilla JavaScript.

## Features

- Add and remove HTTP/HTTPS endpoints
- Run manual availability checks
- View HTTP status and response time
- See average uptime based on recorded checks
- Review the latest 20 checks for each endpoint
- Responsive dark dashboard
- SQLite storage; no external database required

## Requirements

- Python 3.10 or newer
- pip

## Run locally

1. Clone or download this repository.
2. Open a terminal in the project folder.
3. (Optional) Create and activate a virtual environment.
4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the app:

   ```bash
   python app.py
   ```

6. Open http://127.0.0.1:5000 in your browser.

The SQLite database (`pulse.db`) is created automatically on first run.

## API routes

| Method | Route | Purpose |
|---|---|---|
| GET | `/` | Dashboard |
| POST | `/api/endpoints` | Add an endpoint |
| POST | `/api/endpoints/<id>/check` | Run a manual check |
| GET | `/api/endpoints/<id>/history` | Read recent check history |
| DELETE | `/api/endpoints/<id>` | Delete an endpoint |

## Important security note

This is an educational portfolio project, not a production-ready public monitoring service. It accepts only public HTTP/HTTPS targets, checks DNS results against non-public IP ranges, uses request timeouts, and does not follow redirects. However, DNS rebinding and other server-side request forgery risks require stronger network-level controls than this small demo provides.

Before exposing it to the public internet, add authentication, CSRF protection, rate limiting, background job isolation, strict egress/network controls, and robust DNS/IP pinning. Do not deploy it as a public service in its current form.

## Current scope

Checks are manual; there is no scheduler, alerting, or charting yet. Uptime percentages are calculated from the checks stored in the local database.

## License

MIT. See [LICENSE](LICENSE).
