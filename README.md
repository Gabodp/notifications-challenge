# Notifications API

[![Tests and coverage](https://github.com/Gabodp/notifications-challenge/actions/workflows/coverage.yml/badge.svg)](https://github.com/Gabodp/notifications-challenge/actions/workflows/coverage.yml)
[![Coverage Status](https://coveralls.io/repos/github/Gabodp/notifications-challenge/badge.svg?branch=main)](https://coveralls.io/github/Gabodp/notifications-challenge?branch=main)

A REST API built with FastAPI for creating and managing notifications across email, SMS, and push channels.

Users can register, authenticate with JWT tokens, and manage their own notifications. Notifications use SQLAlchemy joined-table inheritance so each channel can store its specific delivery information.

---

## Table of contents

- [Features](#features)
- [Architecture](#architecture)
- [Technology](#technology)
- [Requirements](#requirements)
- [Local setup](#local-setup)
- [API routes](#api-routes)
- [Tests](#tests)
- [Database commands](#database-commands)
- [Author](#author)

---

## Features

### Users

- Register with a name, username, email, and password
- Authenticate using an email and password
- Retrieve public user information
- Retrieve the authenticated user's profile
- Update or delete your own account
- Retrieve notifications created by a user
- Password hashing and JWT authentication

### Notifications

- Create email, SMS, and push notifications
- Retrieve all notifications or one notification
- Partially update owned notifications
- Update channel-specific properties
- Delete owned notifications

Delivery strategies are scaffolded for each channel. Integration with real
email, SMS, or push providers is outside the current scope.

---

## Architecture

- **Joined-table inheritance:** common fields live in `notifications`, while email, SMS, and push
each have their own table for their specific fields. I chose this instead of Single table inheritance (STI)
because it would be less messy as we add more channels and more custom fields.
- **SQLAlchemy polymorphism:** the `channel` column works as a discriminator. SQLAlchemy reads it and returns the correct notification type automatically.
- **Strategy pattern:** For scalable purposes, it made sense to follow a strategy pattern on each channel's sending method, as it will also be easy to add a new channel afterwards.

---

## Technology

- Python 3.11+
- FastAPI
- Pydantic + SQLAlchemy
- PostgreSQL 18
- Alembic
- JWT authentication
- Docker Compose
- uv

---

## Requirements

Install:

- [Python](https://www.python.org/) 3.11 or newer
- [uv](https://docs.astral.sh/uv/)
- [Docker](https://www.docker.com/)

The FastAPI application runs locally. Docker runs only PostgreSQL.

---

## Local setup

Install the project dependencies:

```sh
uv sync --dev
```

Create a `.env` file in the project root:

```env
POSTGRES_PASSWORD=admin
DATABASE_URL=postgresql+psycopg://admin:admin@localhost:5432/notifications
SECRET_KEY=replace-this-with-a-secure-secret
```

`POSTGRES_PASSWORD` and the password in `DATABASE_URL` must match.

Start PostgreSQL:

```sh
docker compose up -d
```

Apply the database migrations:

```sh
uv run alembic upgrade head
```

Start the FastAPI development server:

```sh
uv run fastapi dev
```

The application is available at:

- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>
- Users API: <http://127.0.0.1:8000/api/users>
- Notifications API: <http://127.0.0.1:8000/api/notifications>

---

## API routes

### Users

| Method | Path | Authentication | Description |
| --- | --- | --- | --- |
| `POST` | `/api/users` | No | Register a user |
| `POST` | `/api/users/token` | No | Log in and obtain a JWT |
| `GET` | `/api/users/me` | Yes | Get the authenticated user |
| `GET` | `/api/users/{user_id}` | No | Get public user information |
| `PATCH` | `/api/users/{user_id}` | Owner | Update a user |
| `DELETE` | `/api/users/{user_id}` | Owner | Delete a user |
| `GET` | `/api/users/{user_id}/notifications` | No | Get a user's notifications |

### Notifications

| Method | Path | Authentication | Description |
| --- | --- | --- | --- |
| `GET` | `/api/notifications` | No | List notifications |
| `GET` | `/api/notifications/{notification_id}` | No | Get a notification |
| `POST` | `/api/notifications` | Yes | Create a notification |
| `PATCH` | `/api/notifications/{notification_id}` | Owner | Partially update a notification |
| `DELETE` | `/api/notifications/{notification_id}` | Owner | Delete a notification |

---

## Tests

Tests use a separate PostgreSQL database named `test_notifications`.

Create it once:

```sh
docker compose exec postgres \
  createdb -U admin -O admin test_notifications
```

Run the complete test suite:

```sh
uv run pytest -v
```

Pushes to `main` and pull requests run the tests with Coverage.py and upload
the resulting report to Coveralls through GitHub Actions.

The tests replace FastAPI's normal database dependency with a test session.
Each test runs inside an isolated transaction that is rolled back afterward.

The current test configuration expects the default local credentials:

```text
user: admin
password: admin
database: test_notifications
```

---

## Database commands

Connect to the development database:

```sh
docker compose exec postgres \
  psql -U admin -d notifications
```

List tables from inside `psql`:

```sql
\dt
```

Stop PostgreSQL while preserving its data:

```sh
docker compose down
```

PostgreSQL data is stored in a Docker named volume. Initialization variables
such as `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` only take effect
when that volume is created for the first time.

---

## Author

**Gabriel del Pino**

- GitHub: [@Gabodp](https://github.com/Gabodp)
- LinkedIn: [Add LinkedIn profile](https://www.linkedin.com/in/your-profile)
