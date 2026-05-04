# Security Dashboard — Mini SOC System

A lightweight Security Operations Center (SOC) dashboard that logs login events, detects suspicious activity using rule-based heuristics, and visualises everything in a real-time React UI.

---

## Quick Start

```bash
# Clone and launch
git clone <your-repo>
cd security-dashboard
docker compose up --build

# Frontend → http://localhost:3000
# Backend API → http://localhost:8000
```

Run the attack simulator:

```bash
cd attack-simulator
pip install requests
python attack.py                        # 10 failed logins, default IP
python attack.py --count 15 --mixed    # 15 failures + legit traffic
python attack.py --url http://localhost:8000 --ip 10.0.0.99 --count 20
```

---

## Problem

Security teams need fast visibility into abnormal authentication patterns. Brute-force and credential-stuffing attacks are high-volume and time-sensitive — a tool that ingests login events, applies detection rules in real time, and surfaces flagged IPs without requiring a SIEM or ML pipeline is useful for small teams and home labs.

---

## Approach

### Backend (Django + DRF)

Each `POST /login-attempt` call:

1. Persists the event to SQLite via the `LoginEvent` model.
2. Calls `detection.is_suspicious(ip)` which applies two rules:
   - **Brute-force rule**: >5 failed attempts from the same IP in the last 5 minutes.
   - **Rate rule**: >10 total requests from the same IP in the last 60 seconds.
3. If flagged, all events from that IP are back-filled with `is_suspicious=True`.

The `/events`, `/suspicious`, and `/stats` endpoints expose the data for the frontend.

### Frontend (React)

- **Events tab**: live table of all events, auto-refreshes every 5 seconds, suspicious rows highlighted in amber.
- **Suspicious tab**: filtered view of flagged events only.
- Stat cards at the top show total / success / fail / suspicious counts.
- No external state library — plain `useState` / `useEffect` with polling.

### Infrastructure

- Docker Compose orchestrates `backend` (Django) and `frontend` (nginx serving React build).
- nginx proxies `/login-attempt`, `/events`, `/suspicious`, `/stats` to the backend container so the frontend never needs CORS.
- GitHub Actions runs backend tests and builds both Docker images on every push.

---

## API Reference

| Method | Path             | Description               |
| ------ | ---------------- | ------------------------- |
| POST   | `/login-attempt` | Record a login attempt    |
| GET    | `/events`        | All events (newest first) |
| GET    | `/suspicious`    | Flagged events only       |
| GET    | `/stats`         | Aggregate counts          |

**POST `/login-attempt` payload:**

```json
{
  "ip": "192.168.1.1",
  "username": "admin",
  "success": false
}
```

---

## Limitations

- **SQLite is single-writer**: fine for a demo, but concurrent write spikes under load will produce lock errors. Replace with PostgreSQL for production.
- **In-process detection**: the detection query runs synchronously inside the request cycle. Under high throughput this adds latency. A queue (Celery + Redis) would decouple ingestion from analysis.
- **No authentication**: the API is open. Add token auth (DRF `TokenAuthentication`) before exposing this outside a local network.
- **No persistence across restarts (Docker volume)**: the SQLite file lives inside the container. Mount a named volume or switch to an external DB.
- **Polling, not push**: the frontend polls every 5 s. Replace with WebSockets (Django Channels) for genuinely real-time updates.
- **IP spoofing**: the API trusts the `ip` field in the request body. In a real deployment, read the IP from `X-Forwarded-For` or `REMOTE_ADDR`.

---

## Future Improvements

- **Persistent storage**: PostgreSQL + named Docker volume.
- **Real-time frontend**: WebSocket feed via Django Channels.
- **Alerting**: email / Slack webhook when an IP is flagged.
- **Geo-IP enrichment**: resolve IPs to country/ASN for the event table.
- **More detection rules**: user-agent anomalies, distributed attacks across many IPs, impossible travel.
- **Admin UI**: Django admin or a custom management page to clear flags / whitelist IPs.
- **Auth**: protect the dashboard and the API behind login.
- **Export**: CSV / JSON download of event logs.

---

## Running Tests Locally

```bash
cd backend
pip install -r requirements.txt
python manage.py test app --verbosity=2
```
