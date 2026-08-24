# Railroad Operations

The operation package is the application-independent operational API over persisted railroad assets.

It is intentionally independent of Flask, REST, CLI, mobile UI, or other service adapters.

Core operations are:

- `Asset(config).view(id)` — load and bind an object, including retired objects.
- `asset.update()` — persist changes to a bound domain object.
- `asset.retire()` — set `asset.model.status` to `Status.RETIRED` and persist it.
- `Asset(config).create(...)` — allocate an ID, construct a domain object through a caller-supplied builder, and persist it.
- `Roster.from_config(config).search(criteria)` — search a populated active roster and return IDs only.

Retired objects are excluded when an operational roster is populated, but `view(id)` does not apply that filter.
