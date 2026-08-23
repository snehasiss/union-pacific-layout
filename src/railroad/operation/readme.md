# Railroad Operations

The operation package is the application-independent operational API over persisted railroad assets.

It is intentionally independent of Flask, REST, CLI, mobile UI, or other service adapters.

Core operations are:

- `view(id)` — load and return the domain object, including retired objects.
- `update(obj)` — persist a modified domain object.
- `retire(obj)` — set `obj.model.status` to `Status.RETIRED` and persist it.
- `create(...)` — allocate an ID, construct the domain object through a caller-supplied builder, and persist it.
- `Roster.search(...)` — search a populated active roster and return IDs only.

Retired objects are excluded when an operational roster is populated, but `view(id)` does not apply that filter.
