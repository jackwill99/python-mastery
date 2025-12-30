"""
# Migration Playbook: NestJS/Flutter -> Python

## Senior Pro-Tip
- Python stack mirrors NestJS (FastAPI + Pydantic + SQLAlchemy) and Flutter clients via OpenAPI/JSON; emphasize typed DTOs and async drivers for parity.

## Data Migration
- Use dual-writes: keep NestJS live, add Python service writing to new tables/columns.
- Backfill with idempotent jobs; track progress in a control table.
- Validate with row counts + checksums; run shadow reads via feature flags.

## API Versioning
- Keep v1 (NestJS) stable; expose v2 (Python) under /v2 with strict schemas.
- Use a traffic splitter (gateway) to shift percentages; log mismatches.

## Zero-Downtime Deployment
- Blue/green or rolling with health checks.
- Migrations in safe steps: add nullable, backfill, set not null, swap reads, drop legacy.
- Feature flags for risky behavior (e.g., dual writes, new payment provider).

## Example: Dual-Write Snippet
```python
async def create_user(payload):
    await nestjs_client.post("/v1/users", json=payload)  # legacy
    await python_client.post("/v2/users", json=payload)  # new
```

## Observability
- Structured logging + correlation IDs.
- Tracing via OpenTelemetry (Jaeger/Honeycomb).
- Metrics: request latency, error rates, migration lag.

## Rollback
- Keep DB backups + feature flags.
- If v2 misbehaves, route 100% traffic back to v1 and stop dual writes.
"""

