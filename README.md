# Pulse — API Monitor

Pulse is a lightweight, responsive API and website monitoring dashboard built with Flask and SQLite.

## Features

- Add, check, and delete monitored endpoints
- Public HTTP/HTTPS URL validation
- Private and local-network SSRF protection
- HTTP status codes and response-time tracking
- Uptime percentages and recent check history
- Responsive dashboard with no frontend framework
- SQLite storage with automatic schema initialization

## Project structure

```text
api-monitor/
├── app/
│   ├── __init__.py
│   ├── static/
│   │   ├── app.js
│   │   └── style.css
│   └── templates/
│       └── index.html
├── tests/
│   └── test_app.py
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── run.py
```

## Requirements

- Python 3.10 or newer
- pip

## Run locally

```bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:5000.

The SQLite database is stored at `pulse.db` and is created automatically.

## Tests

```bash
python -m unittest discover -s tests -v
```

## API

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/` | Dashboard |
| `GET` | `/health` | Application health check |
| `POST` | `/api/endpoints` | Add an endpoint |
| `POST` | `/api/endpoints/<id>/check` | Run a check |
| `GET` | `/api/endpoints/<id>/history` | Read recent history |
| `DELETE` | `/api/endpoints/<id>` | Delete an endpoint |

## Security

This is an educational, local-first monitoring application—not a production service. It validates public HTTP/HTTPS targets before every check and blocks private, loopback, link-local, reserved, multicast, and unspecified IP addresses.

Before public deployment, add authentication, CSRF protection, rate limiting, persistent scheduler isolation, strict outbound networking, and a production WSGI server.

## License

MIT. See [LICENSE](LICENSE).
