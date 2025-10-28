# Secret Santa

A full-stack Secret Santa web application with a FastAPI backend and a React + Vite frontend. The project ships with Docker Compose for local development and production deployment.

## Features

- Create private Secret Santa groups with secure join URLs and PINs.
- Participants can join with optional household, interests, and no-go gift details.
- Organizers manage exclusions and trigger fair draws that respect all constraints.
- Celery worker sends personalized assignment emails using Jinja2 templates.
- Anonymous Q&A channel between gifters and receivers.
- Dockerized stack with FastAPI, PostgreSQL, Redis, and a Celery worker.

## Getting Started

### Prerequisites

- Docker and Docker Compose installed locally.
- Copy `backend/.env.example` to `backend/.env` and update secrets, SMTP credentials, and database URLs as needed.

```bash
cp backend/.env.example backend/.env
```

### Running with Docker Compose

From the project root run:

```bash
docker-compose up --build
```

Services included:

- `api`: FastAPI application served by Uvicorn.
- `worker`: Celery worker for background email tasks.
- `db`: PostgreSQL database.
- `redis`: Redis broker for Celery.
- `frontend`: Vite development server (or static build in production).
- `reverse-proxy`: Caddy serving HTTPS (self-signed locally).

The API is available at `http://localhost:8000` and the frontend at `http://localhost:5173` during development.

### Database Migrations

Alembic migrations are located under `backend/alembic`. To apply migrations inside the API container:

```bash
docker-compose run --rm api alembic upgrade head
```

### Running Frontend in Development

To run the frontend locally outside of Docker:

```bash
cd frontend
npm install
npm run dev
```

The development server proxies API requests to the FastAPI container.

### Testing the Pairing Algorithm

A standalone script is not provided, but you can import `make_assignments` from `backend/app/services/pairing.py` and supply member dictionaries with exclusions to ensure constraints are satisfied.

## Deployment Notes

- Configure SMTP credentials for real email delivery and set up SPF/DKIM/DMARC on your domain.
- Update `join_url` generation in `backend/app/routes/groups.py` to use your production domain.
- Configure Caddy or NGINX TLS certificates for HTTPS in production.
- Schedule database backups and monitor Celery worker health.
