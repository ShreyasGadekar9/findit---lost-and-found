# FindIt Java API

FindIt pairs lost-item reports with found-item reports, checks an owner-provided private detail before enabling chat, and closes a case after both sides confirm the return.

## Run

From the workspace root:

```sh
pnpm --filter @workspace/api-server run dev
```

The managed API workflow starts this Spring Boot service on the configured port, mounted at `/api`. The React app runs separately at `/`.

For a local Java run, the development PostgreSQL variables (`PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, and `PGPASSWORD`) must be available. Apply schema changes through the workspace's Drizzle schema:

```sh
pnpm --filter @workspace/db run push
cd apps/findit-java
mvn spring-boot:run
```

## Matching

Every new report is compared with open reports of the opposite type. The MVP score combines category match (25%), description/title word overlap (45%), location word overlap (20%), and time proximity (10%). Found dates before the reported lost date are rejected; candidates scoring at least 0.34 are surfaced.

Image embeddings, map-distance scoring, authentication, and account-specific message access are not part of this prototype yet. Demo rows are inserted only when explicitly enabled on an empty database:

```sh
cd apps/findit-java
mvn spring-boot:run -Dspring-boot.run.arguments=--findit.seed-demo=true
```

The sample match can be verified with `small blue stitch`; that value exists only to let someone walk through the demo and must not be used as a real user's verification detail.

## API

- `GET /api/healthz`
- `GET /api/dashboard`
- `GET /api/items?type=LOST&q=wallet&status=OPEN`
- `POST /api/items`
- `GET /api/matches`
- `POST /api/matches/{matchId}/verify`
- `GET|POST /api/matches/{matchId}/messages`
- `POST /api/matches/{matchId}/confirm-return`
