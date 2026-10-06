# FindIt Lost & Found

FindIt helps people report lost and found items, discover likely matches, verify an owner with a private detail, and coordinate returns without sharing phone numbers.

## Run & Operate

- `pnpm --filter @workspace/findit run dev` — run the web app at `/`
- `pnpm --filter @workspace/api-server run dev` — run the Java Spring Boot API at `/api`
- `pnpm --filter @workspace/findit run typecheck` — typecheck the web app
- `pnpm run typecheck` — typecheck the workspace TypeScript packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and schemas from OpenAPI
- `pnpm --filter @workspace/db run push` — apply the current Drizzle schema to the development database
- Java API requires the workspace PostgreSQL variables (`PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`)

## Stack

- Web app: React, Vite, TypeScript, generated React Query API hooks
- API: Java 17+ with Spring Boot, JDBC, and PostgreSQL
- Database schema source: Drizzle in `lib/db/src/schema/`
- API contract source: `lib/api-spec/openapi.yaml`

## Where things live

- `artifacts/findit` — responsive FindIt web app
- `apps/findit-java` — Java API, matching logic, and demo seed data
- `lib/api-spec/openapi.yaml` — API contract
- `lib/db/src/schema/items.ts` — lost/found reports, matches, and messages
- `artifacts/api-server` — managed `/api` workflow that runs the Java service

## Architecture decisions

- Matching and ownership verification run in Java; the UI uses generated API hooks from the shared OpenAPI contract.
- Public report responses omit the private verification detail. Chat endpoints reject requests until the match is verified.
- The current app is a prototype: authentication and participant-only chat permissions must be added before using it with public users.

## Product

- Supports lost and found reports with locations, descriptions, optional image URLs, and private verification details.
- Scores likely matches using category, text, location, and date proximity.
- Opens a chat after verification and closes a case after both owner and finder confirm the return.

## Gotchas

- Schema updates belong in Drizzle and apply to the development database with `pnpm --filter @workspace/db run push`; do not add application-startup DDL.
- The demo's sample private detail is `small blue stitch`; it is not suitable as a real account credential.
