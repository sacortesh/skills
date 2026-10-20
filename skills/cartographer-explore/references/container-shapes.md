# Suggested container sets, by software shape

## Contents
- Client app
- Server / backend
- Worker / background job system
- Pipeline
- Embedded system
- Middleware
- CI/CD or DevOps pipeline

These are starting points to offer the user during Step 0, never a forced
taxonomy. The goal of Step 0 is discovering the *real* containers in the
project at hand — if what you find disagrees with the table below, the real
project wins every time. Treat these as a faster way to ask the right first
question, not as ground truth.

For each shape: the suggested containers, in the order they usually make
sense to check, and what "state" tends to mean for that shape (since a
feature's state machine looks very different depending on the shape).

## Client app (web, mobile, desktop, game)

| Container | What lives here |
|---|---|
| Data | Local state shape — what's persisted (localStorage, save file, on-device DB) vs. purely in-memory |
| Domain/Logic | Business rules, independent of how they're displayed |
| Interface | UI/rendering, user interaction |
| Backend/API *(only if it talks to a server)* | The contract with the remote side — don't add this container if the app is genuinely standalone |

State usually means: UI state (loading/error/success), or domain state
(an entity's lifecycle — e.g. a game character's mood, an order's status).

## Server / backend

| Container | What lives here |
|---|---|
| Data | Schema, persistence, migrations |
| Domain/Logic | Services, business rules |
| API/Interface | Endpoints, request/response contracts |
| Background jobs *(only if async work exists)* | Anything not handled inline in a request |

State usually means: an entity's lifecycle in the data layer, or a request's
processing state if there's meaningful async handling.

## Worker / background job system

| Container | What lives here |
|---|---|
| Trigger | What starts the job — cron, queue message, webhook, event |
| Processing/Logic | The job's actual rules |
| Data | What it reads and writes |
| Failure handling | Retry policy, backoff, dead-letter behavior |

State is usually the job's own lifecycle, and it's almost always worth a
diagram even for a simple worker: `pending → processing → succeeded /
failed → retrying → dead-lettered`. This is frequently the single most
valuable diagram in the whole system, because failure/retry logic is where
silent bugs hide.

## Pipeline (batch processing, CLI tools with sequential stages, media/data pipelines)

| Container | What lives here |
|---|---|
| Trigger/Input | What starts a run and what it takes in |
| Stages | The ordered sequence of processing steps |
| Data/Artifacts | What's produced at each stage boundary — intermediate files, in-memory objects passed between stages |
| Failure/Recovery | What happens if a stage fails partway through — does it clean up, resume, or leave partial output? |

State is the position in the stage sequence. Treat each stage transition as
a real state-machine edge, especially "what happens if this stage throws" —
pipelines built as a single top-to-bottom script often have no explicit
failure state at all, which is itself worth documenting as a finding, not
silently working around. A pipeline's stage sequence is also the clearest
case for the `sequenceDiagram` alternative in Step 3 of the main skill — a
stage-by-stage flow usually reads more naturally as a sequence than as a
state machine, since there's rarely any branching back to an earlier stage.

## Embedded system

| Container | What lives here |
|---|---|
| Hardware/Driver | Physical I/O this touches directly |
| Firmware/RTOS | Scheduling, interrupts, low-level state |
| Application logic | The actual feature behavior |

There is often no "Interface" container in the UI sense — physical outputs
(an LED, an actuator, a display segment) *are* the interface. Don't force a
UI section; document the physical output as part of Application logic or as
its own small "Physical interface" note if it's non-trivial.

## Middleware (API gateway, auth layer, message broker, proxy)

| Container | What lives here |
|---|---|
| Input contract | What it receives, from whom |
| Transformation/Rule | What it does to the input — auth check, routing, rate-limiting, transformation |
| Output contract | What it passes downstream, and to where |
| Internal state *(if any)* | e.g. a circuit breaker's own state, a rate-limiter's counters |

Middleware state machines are often small but critical — a circuit breaker
(`closed → open → half-open`) is the canonical example. If the middleware
looks stateless, verify that's actually true rather than assuming it. An
auth or routing check, by contrast, is usually better shown as a
`sequenceDiagram` (request in, checks performed in order, response or
rejection out) than forced into a state machine it doesn't really have.

## CI/CD or DevOps pipeline

| Container | What lives here |
|---|---|
| Trigger | What starts a run — push, PR, schedule, manual dispatch |
| Stages | The pipeline's own state machine — e.g. `queued → linting → testing → building → deploying → succeeded/failed` |
| Environment/Config | What varies per environment (staging vs. prod, secrets, feature flags) |
| Rollback/failure path | What happens on failure — does anything auto-revert, alert, or block? |

This shape is almost identical to the generic Pipeline shape above; the
difference is usually that CI/CD systems have richer environment/config
variation worth its own layer, and a rollback path is almost always worth
documenting explicitly even if "rollback" just means "nothing happens
automatically" — that absence is itself a fact worth stating plainly rather
than leaving implicit.
