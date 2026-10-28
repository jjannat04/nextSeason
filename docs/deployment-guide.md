# Deployment guide — current React/Vite + Django stack

This is a concrete **single Linux VM** deployment recipe. It serves the Vite build and Django API from one HTTPS origin through Nginx. The prototype has no application database, migrations or media uploads. Deploy only `frontend/dist`, `backend`, `data/normalized`, `data/crosswalk`, and Python dependencies; the research, design, tests and Markdown documentation stay in the source repository and are not copied to the public web root. Do not use Vite preview or Django `runserver` as production servers.

## 1. Prepare the host and release

Use a supported Linux VM with DNS pointing the chosen hostname to it, Node.js 24+, Python 3.12+, Nginx, a TLS certificate and a non-root service account named `nextseason`. Substitute your actual domain for `nextseason.example.org` in commands/configuration. Keep `/srv/next-season/app` readable by the service, and `/srv/next-season/cache` writable only by the service. The Nginx worker only needs read access to `frontend/dist`.

```bash
sudo apt update
sudo apt install -y python3-venv nginx
sudo useradd --system --home /srv/next-season --shell /usr/sbin/nologin nextseason
sudo mkdir -p /srv/next-season/app /srv/next-season/cache/power /srv/next-season/cache/environment
sudo chown -R nextseason:nextseason /srv/next-season
# Transfer a reviewed source checkout to /srv/next-season/app; exclude .env, .runtime, .venv, node_modules and dist.
cd /srv/next-season/app
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
.venv/bin/python -m pip install gunicorn
cd frontend
npm ci
npm test
npm run build
cd ..
PYTHONPATH=backend .venv/bin/python -m unittest discover -s tests
```

For repeatable production releases, record the reviewed Gunicorn version in the deployment lock/manifest before promotion. The current `backend/requirements.txt` contains application dependencies but no WSGI server. If tests are run on the host, transfer `tests` too; otherwise run them in CI or the release staging workspace before transferring the minimal artifact.

## 2. Backend environment and service

Create `/etc/next-season/backend.env` through the host's secret-management process, readable only by root and the service. Give it real values for `DJANGO_SECRET_KEY` (long random value), `DJANGO_ALLOWED_HOSTS` (exact hostname), `EARTHDATA_TOKEN` (backend only), `NEXTSEASON_DEBUG=0`, `NEXTSEASON_ALLOW_FIXTURES=0`, `NEXTSEASON_CACHE_DIR=/srv/next-season/cache/power`, `NEXTSEASON_ENV_CACHE_DIR=/srv/next-season/cache/environment`, `NEXTSEASON_SECURE_SSL_REDIRECT=1`, `NEXTSEASON_HSTS_SECONDS=3600`, and `NEXTSEASON_TRUST_PROXY_HEADERS=1`. Never place credentials in Git, `frontend/`, Nginx files, command arguments, or the public document root. Do not use `NASA_APPEEARS_TOKEN` unless separately authorized and validated; the live validated Harmony path uses `EARTHDATA_TOKEN` (or `NASA_EARTHDATA_TOKEN`).

The proxy-header setting is safe only when Gunicorn listens on loopback and Nginx **overwrites** `X-Forwarded-Proto`; never expose Gunicorn directly. Start with a short HSTS duration; increase it only after HTTPS has been stable. `check --deploy` may still warn about HSTS include-subdomains/preload; those require deliberate ownership of every subdomain, not automatic enabling.

Create `/etc/systemd/system/next-season.service`:

```ini
[Unit]
Description=Next Season Django API
After=network-online.target
Wants=network-online.target

[Service]
User=nextseason
Group=nextseason
WorkingDirectory=/srv/next-season/app
Environment=PYTHONPATH=/srv/next-season/app/backend
EnvironmentFile=/etc/next-season/backend.env
ExecStart=/srv/next-season/app/.venv/bin/gunicorn --chdir /srv/next-season/app/backend --bind 127.0.0.1:8001 --workers 2 --timeout 120 config.wsgi:application
Restart=on-failure
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

Use systemd credentials or another secret store if available. Ensure the service can read its environment file without making it world-readable. NASA Harmony jobs can outlast one HTTP request and are polled on later calls; the 120-second WSGI timeout does not guarantee a provider job completes in one response.

Before service startup, run checks using the same environment **without echoing it**. An operator can load the file into an isolated shell or use an equivalent service-run command. Check `manage.py check --deploy`, then verify `GET /api/health` after startup. No `migrate` operation is required: there are no application models or migrations and no database configured.

## 3. Same-origin static and API routing

The frontend calls relative `/api` URLs. `NEXTSEASON_API_TARGET` is a Vite **development proxy** setting and is not a production API base URL. Do not build with an Earthdata token or expose a separate cross-origin API. No broad CORS configuration is needed for same-origin requests.

Create an Nginx site with the following server block after obtaining a valid TLS certificate. Adjust certificate paths and hostname. The HTTP port-80 site should redirect to HTTPS using your certificate tool's normal configuration.

```nginx
server {
    listen 443 ssl;
    server_name nextseason.example.org;
    ssl_certificate /etc/letsencrypt/live/nextseason.example.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/nextseason.example.org/privkey.pem;
    root /srv/next-season/app/frontend/dist;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 125s;
    }
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Hash public routes such as `/#/methodology` resolve within the frontend; Nginx serves `index.html`. Do not expose `/srv/next-season/app` or cache directories as web roots. The application has no Django static/media collection step.

```bash
sudo nginx -t
sudo systemctl daemon-reload
sudo systemctl enable --now next-season
sudo systemctl reload nginx
curl -fsS https://nextseason.example.org/api/health
```

Inspect the health JSON: `fixtures_enabled` must be `false` and `recommendation_mode` must be `prototype_recommendation`. Production requests should return JSON errors, never Django debug pages. Check a real plan and environmental profile using the accepted request bodies from the browser/API tests; never send credentials to the API. The provider token exists only in the backend environment. The Nginx API path must retain its `/api/` prefix because Django routes include it.

## 4. Cache, failure and rollout checks

- Keep both cache directories private, writable and persistent across deployments. POWER and satellite cache keys include relevant product, point and period parameters; the satellite cache retains provenance/checksums. Do not copy cache contents into the public root or a Git commit.
- Warm and repeat the **same exact point/period** at three Bangladesh locations. The initial uncached SMAP/IMERG call may return a pending provider state; poll subsequent requests until available or a documented failure/timeout. Never interpret unavailable as zero.
- Inspect server logs for statuses and latency only. Never enable full request-header logging or put Authorization headers into access logs.
- Verify HTTPS, `/api/health`, a normal plan, partial-provider failure, public routes/refresh/history, browser network responses, and A4 print/PDF using `release-checklist.md`.
- A release is not complete until the human acceptance checklist is signed off. Keep the previous deployment artifact for rollback; roll back app and frontend together, while retaining private NASA caches.
