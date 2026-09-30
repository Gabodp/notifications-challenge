## Local PostgreSQL

The FastAPI app runs on your machine. Docker Compose runs only PostgreSQL and
stores its data in a named volume.

If another PostgreSQL container is already using port 5432, stop it first with
`docker stop <container-name>`. Then start this database:

```sh
docker compose up -d
uv run alembic upgrade head
```

The Compose defaults are database `notifications`, user `admin`, and password
`admin`, matching a local `DATABASE_URL` of
`postgresql+psycopg://admin:admin@localhost:5432/notifications`. For a different
password, set `POSTGRES_PASSWORD` before starting Compose and use the same
password in `DATABASE_URL`.

Connect with `docker compose exec postgres psql -U admin -d notifications`, then
use `\dt` to list tables. `docker compose down` stops the database while keeping
the volume. This named volume starts empty; it does not contain data from a
PostgreSQL container previously started with `docker run`.
