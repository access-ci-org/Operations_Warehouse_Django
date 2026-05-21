# WAREHOUSE_AGENTS.md
## AI Agent Instructions — ACCESS Operations Warehouse Django

---

## PRIME DIRECTIVE

**Default to PLAN mode. Always.**

Before writing a single line of code, generate a numbered plan and wait for human approval. This codebase serves live production infrastructure. One wrong migration, one broken serializer, one mis-routed URL can cascade across multiple integrated services. Pause, plan, confirm — then implement **one step at a time**.

### What "One Step at a Time" Means Here

- **One step = one file changed, or one logical unit of work**, not a batch of related changes bundled together.
- After each step: stop, show what changed, check for errors, and ask the human if it looks right before continuing.
- If a task naturally has 5 steps, do not jump ahead to step 3 because step 2 felt obvious. Always surface each step explicitly.
- Never chain multiple `replace_string_in_file` calls across different logical concerns in a single turn without labeling each one as a distinct step.
- If you realize mid-execution that a step is larger than originally scoped, **stop and re-plan** before continuing.

### What "Methodical Reasoning" Means Here

- Before touching any file, state your **mental model** of how the system currently works for the relevant area.
- Trace the data flow: where does data come from, what transforms it, where does it go? Name the specific models, serializers, views, and templates involved.
- Explicitly state any **assumptions** you are making. If an assumption could be wrong, flag it as a question.
- If two approaches exist, name both, explain the tradeoff, and recommend one — don't silently pick one.
- Think out loud about **side effects**: what else in the codebase could be affected by this change?

---

## Project Overview

This is the **ACCESS Operations (CONECT) Service-Facing Information Sharing Platform** — a Django 5.2 application that aggregates and exposes information about ACCESS integrated cyberinfrastructure resources.

It is simultaneously:
- A **REST API** (Django REST Framework + drf-spectacular / OpenAPI)
- A **developer-facing web UI** (Django templates, Bootstrap 5)
- A **search index host** (AWS OpenSearch / Elasticsearch 7.10)
- A **relational data warehouse** (AWS Aurora PostgreSQL 15)
- A **processing activity tracker** (warehouse_state)
- A **badge/roadmap compliance tracker** (integration_badges)

**Version:** 3.72.0  
**Python:** 3.12  
**Django:** 5.2  

---

## Directory Map — Know Before You Touch

```
Operations_Warehouse_Django/          ← repo root (git root, .gitignore lives here)
└── Operations_Warehouse_Django/      ← Django project root (manage.py lives here)
    ├── Operations_Warehouse_Django/  ← Django config package (settings, urls, wsgi, asgi)
    │   ├── settings.py               ← APP_CONFIG env var required; reads JSON conf file
    │   ├── urls.py                   ← Root URL router — all apps mount at /wh2/<app>/
    │   ├── views.py                  ← Debug_Dump view
    │   ├── wsgi.py / asgi.py
    │   └── __init__.py
    ├── allocations/                  ← ACCESS allocation & person data (AMIE/XDCDB mirror)
    ├── cider/                        ← CiDeR infrastructure resource catalog
    ├── glue2/                        ← GLUE2 standard HPC resource descriptions
    ├── integration_badges/           ← Roadmap badge/task compliance tracking
    ├── integration_views/            ← Pivot/aggregation views across apps
    ├── news/                         ← Outage, maintenance, and release news items
    ├── resource_v4/                  ← Unified resource discovery (DB + OpenSearch index)
    ├── roadmap_pivot/                ← Template tags for roadmap pivot tables
    ├── warehouse_state/              ← Processing activity and error tracking
    ├── warehouse_tools/              ← Shared exceptions, responses, pagination
    ├── web/                          ← Public web UI (docs, browse pages)
    ├── templates/                    ← Base and shared templates
    ├── static/                       ← CSS, fonts, images
    └── manage.py
```

**The triple-nested `Operations_Warehouse_Django/` is a frequent source of confusion.**  
- Git root → `Operations_Warehouse_Django/` (the repo clone directory)  
- Django `manage.py` → `Operations_Warehouse_Django/Operations_Warehouse_Django/`  
- Django settings/urls → `Operations_Warehouse_Django/Operations_Warehouse_Django/Operations_Warehouse_Django/`  

When an agent or human says "the settings file", they mean the third level.

---

## Application Inventory — Each App's Role

### `allocations`
Mirrors AMIE/XDCDB allocation and person data. Key models: `Resource`, `Person`, `PersonLocalUsernameMap`, `AllocationResourceMap`, `FieldOfScience`. These records are **ingested from external systems, not created by users**. Do not add write endpoints without explicit discussion of the upstream sync contract.

### `cider`
CiDeR (Cyberinfrastructure Description Repository) infrastructure catalog. Models: `CiderInfrastructure`, `CiderOrganizations`, `CiderFeatures`, `CiderGroups`. Has a `filters.py` for queryset filtering and a `utils.py` for transformations (e.g. `cider_to_coco`). Views use both `TemplateHTMLRenderer` and `JSONRenderer` — changes here affect both the web UI and API consumers.

### `glue2`
GLUE2 standard schemas for HPC resources: `AdminDomain`, `UserDomain`, `ApplicationEnvironment`, `ApplicationHandle`, and more. All models inherit `AbstractGlue2EntityModel` (ID, Name, CreationTime, Validity, EntityJSON). Has a `process.py` for indexing. Data comes from AMQP message publishers — do not remove or rename fields without checking the publisher contract.

### `integration_badges`
Roadmap badge and compliance tracking. Models use `TextChoices` enums (`ResourceStatus`, `BadgeWorkflowStatus`, `BadgeTaskWorkflowStatus`). Depends on `cider.models` (imports `*`). Contains `DatabaseFile`/`DatabaseFileStorage` — files are stored in the database as binary, not on disk. Changes to badge workflow statuses must be coordinated with the roadmap UI and integration teams.

### `integration_views`
Aggregation/pivot views. No models. Views split across `views/resource_pivot_views.py` and `views/group_pivot_views.py`. Serializers in `serializers.py`. These views join data across multiple apps — changes to upstream models can break these silently.

### `news`
Outage, maintenance, and release news. Models: `News`, `News_Associations`, `News_Publisher`. `News_Associations` links news items to Resources, Software, or Roadmap items by `AssociatedType`/`AssociatedID` strings — not FK-enforced, so referential integrity is application-level.

### `resource_v4`
Unified resource discovery layer — the most complex app.
- **Dual storage:** PostgreSQL (via `ResourceV4Local`, `ResourceV4`, etc.) AND OpenSearch (via `ResourceV4Index` document in `documents.py`)
- **`process.py`:** Handles indexing objects into OpenSearch. Any change to `ResourceV4` model fields must be mirrored in `documents.py` and the index mapping.
- **`ResourceV4Catalog`** describes upstream data sources. `ResourceV4Local` is the raw unmodified record. Abstract models provide the standard discovery fields.
- OpenSearch index name: `resource-v4-index`

### `warehouse_state`
Cross-cutting processing activity tracking. `ProcessingActivity` class (in `process.py`) is instantiated by external processing scripts to record start/end/status. `ProcessingStatus` and `ProcessingError` models are the audit trail. Do not delete records from these tables without confirming no tooling depends on them.

### `warehouse_tools`
Shared infrastructure for the API layer:
- `exceptions.py` — `MyAPIException`
- `responses.py` — `MyAPIResponse`, `CustomPagePagination`
These are used across every app. Changes here are global in impact.

### `web`
Developer-facing documentation and browse UI. Has `context_processors.py` and `signals.py`. Template-heavy. Changes here are lower risk but still affect public-facing pages.

---

## Infrastructure & Configuration

### APP_CONFIG (Required)
Settings are **not** in `.env`. The app reads a JSON config file at the path specified by the `APP_CONFIG` environment variable. Without it the app exits immediately. Fields include:
- `DJANGO_SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- `DJANGO_USER`, `DJANGO_PASS`, `DB_NAME`, `DB_HOSTNAME_WRITE`, `DB_HOSTNAME_READ`, `DB_PORT`
- `OPENSEARCH_HOSTS` (optional — app degrades gracefully if absent)
- `SETTINGS_MODE` (default: `'SERVER'`)

Never hardcode config values. Never commit a real config file. Use `*_customized.conf` and `*_customized.sql` naming for local overrides (they are .gitignored).

### Databases
Two database aliases are configured: `default` (write host) and `default.read` (read host). Both point to the same Aurora PostgreSQL cluster by default with different host endpoints. The PostgreSQL `search_path` is set to `info_django,info,public` — schema-qualified queries are intentional, not a bug. `CONN_MAX_AGE=600` means connections persist; factor this into any connection pool changes.

### OpenSearch
`django-opensearch-dsl 0.5.*` wraps AWS OpenSearch (compatible with ES 7.10). The `resource_v4` app owns the `resource-v4-index`. The app has a guard (`if not django_settings.OSCON`) — check whether OpenSearch is available before assuming search endpoints work in dev.

### Auth Stack
- `django-allauth` — social/OAuth login
- `cilogon-tokenauth` — CILogon token authentication for API consumers
- `access-django-user-admin` — ACCESS-specific user admin
- `globus-sdk` — Globus integration
- Per-view authentication classes override the DRF defaults. Always check `authentication_classes` on views before assuming the global auth applies.

### Caching
`pymemcache` is in the dependency list. Some views (e.g. OpenSearch relation lookups) use Django's cache framework. Do not remove cache calls without understanding the performance impact on search views.

---

## URL Structure

| Prefix | App |
|---|---|
| `/` | Redirects to `/docs/` |
| `/accounts/` | allauth |
| `/admin/` | Django admin |
| `/docs/` | `web` app |
| `/wh2/state/` | `warehouse_state` |
| `/wh2/allocations/` | `allocations` |
| `/wh2/cider/` | `cider` |
| `/wh2/integration_badges/` | `integration_badges` |
| `/wh2/glue2/` | `glue2` |
| `/wh2/news/` | `news` |
| `/wh2/resource/` | `resource_v4` |
| `/wh2/integration_views/` | `integration_views` |
| `/wh2/api/schema/` | OpenAPI schema |
| `/wh2/api/schema/swagger-ui/` | Swagger UI |
| `/wh2/api/schema/redoc/` | ReDoc |
| `/access_django_user_admin/` | user admin |

All API endpoints live under `/wh2/`. The `/docs/` prefix is the human web UI.

---

## Key Patterns & Conventions

### Views
- Class-based views throughout (`APIView`, `GenericAPIView`)
- `TemplateHTMLRenderer` + `JSONRenderer` on many views — `?format=json` switches output; the template name is passed to `MyAPIResponse`
- Auth: `IsAuthenticatedOrReadOnly` is the typical default; some endpoints require `IsAuthenticated` with explicit `authentication_classes`
- `extend_schema` decorators from `drf-spectacular` are used for OpenAPI docs — preserve them when editing views

### Models
- Primary keys are often strings (`CharField(primary_key=True)`) — typically URI-style IDs (e.g. GLUE2 IDs)
- `EntityJSON = models.JSONField()` is used across GLUE2 and ResourceV4 models to store the raw upstream record alongside normalized fields
- `auto_now_add` / `auto_now` used for `created_at`/`updated_at` — do not manually set these fields

### Migrations
Migrations live in each app's `migrations/` directory. Migration naming follows Django's auto-generation. Do not hand-edit migration files unless correcting a naming squash. Do not `--fake` migrations in production without DBA sign-off.

### Serializers
Each app has a `serializers.py`. Serializers are used both for API output and for internal data transformation. Changing a serializer field can break both the API contract and internal processing logic simultaneously.

---

## High-Risk Areas — Extra Caution Required

| Area | Risk | Why |
|---|---|---|
| `resource_v4/documents.py` | High | OpenSearch index mapping — field changes require re-index |
| `warehouse_tools/responses.py` | High | Used by every app; API response format is a public contract |
| `warehouse_tools/exceptions.py` | High | Same as above |
| `integration_badges/models.py` | High | `TextChoices` values are stored in DB — renaming breaks existing rows |
| `cider/models.py` | High | Downstream of CiDeR API; field names are externally dictated |
| `allocations/models.py` | High | Mirror of AMIE/XDCDB; field names are externally dictated |
| `warehouse_state/process.py` | Medium | Used by external processing scripts outside this repo |
| Any `migrations/` file | High | Irreversible on Aurora without DBA involvement |
| `settings.py` | High | Single misconfiguration exits the process |

---

## Safe vs. Unsafe Changes

### Generally Safe (lower blast radius)
- Adding new read-only API endpoints
- Adding new template views in `web/`
- Adding `extend_schema` annotations without changing logic
- Adding test cases in any `tests.py`
- Updating static assets (`static/`)
- Adding new `TextChoices` values (appending, not renaming)
- Adding new optional model fields with `null=True, blank=True`

### Requires a Plan First
- Any model field rename or removal
- Any migration that alters column types
- Changes to `warehouse_tools/` (global impact)
- Changes to authentication or permission classes
- Changes to `resource_v4/documents.py` (requires OpenSearch re-index)
- Changes to `integration_badges` `TextChoices` enums
- New `INSTALLED_APPS` entries
- Dependency version bumps (`pyproject.toml`)
- Changes to the root `urls.py`

### Do Not Do Without Explicit Human Approval
- `makemigrations --merge`
- Dropping or squashing migrations
- Changing `search_path` in database OPTIONS
- Modifying `CONN_MAX_AGE` or database routing
- Any change that touches multiple apps simultaneously
- Removing or renaming a URL endpoint (consumers depend on these)

---

## Agent Workflow

### Every Task — Follow This Pattern

```
1. PLAN:    State what you understand the task to be. Correct misunderstandings
            before doing anything else.
2. TRACE:   Walk the data flow end-to-end for the affected area.
            Name every file that will be touched.
3. SCOPE:   Identify which apps/files/models are affected. Be explicit —
            "this touches cider/models.py, cider/serializers.py, and
            integration_badges/models.py" is better than "cider and badges".
4. RISK:    Call out any high-risk areas from the table above.
            State any assumptions you are making.
5. STEPS:   Number each step. One step = one file or one logical unit.
            Write out ALL steps before starting any of them.
6. WAIT:    Post the plan. Wait for human confirmation before writing code.
7. EXECUTE: Implement ONLY step 1. Show the exact change.
8. VERIFY:  Check for errors. Run tests for the affected app.
9. CONFIRM: Ask human to confirm step 1 is correct before moving to step 2.
10. REPEAT: Steps 7-9 for each subsequent step. Never skip ahead.
```

**If a step reveals something unexpected** (a dependency you missed, a field that doesn't exist, a test failure), stop immediately, report what you found, and re-plan before continuing.

### For Migrations Specifically

```
1. Show the model change you intend to make (plain English + code).
2. State which table/column is affected and whether data exists.
3. Confirm whether a corresponding migration is needed (it almost always is).
4. Wait for approval.
5. Run makemigrations --dry-run and show output.
6. Wait for approval to actually run makemigrations.
7. Do NOT run migrate without explicit human instruction.
```

### For OpenSearch Changes

```
1. Identify the field change in models.py.
2. Show the corresponding change needed in documents.py.
3. State whether the index needs to be rebuilt (almost always yes for field changes).
4. Confirm the re-index command and timing with human before executing.
```

---

## Common Local Commands

All commands run from `Operations_Warehouse_Django/Operations_Warehouse_Django/` (where `manage.py` lives).

```bash
# Activate venv (from repo root)
source ../.venv/bin/activate

# Verify APP_CONFIG is set (required before any manage.py command)
echo $APP_CONFIG

# Run dev server
python manage.py runserver

# Create migrations (dry run first)
python manage.py makemigrations --dry-run
python manage.py makemigrations

# Show pending migrations
python manage.py showmigrations

# Run tests for a single app
python manage.py test allocations
python manage.py test cider
python manage.py test resource_v4
# etc.

# Run all tests
python manage.py test

# Check for issues
python manage.py check
```

---

## What Not to Assume

- Do not assume `DEBUG=True` is safe to leave on — `DEBUG` is read from the JSON config file.
- Do not assume a local database is available — the app requires `APP_CONFIG` and a working PostgreSQL connection.
- Do not assume `OpenSearch` is running locally — the app has guards for this, but search-related views will return 503.
- Do not assume all models belong to this codebase — many are read-only mirrors of external system records (CiDeR, AMIE, GLUE2 publishers).
- Do not assume all apps are independent — `integration_badges` imports from `cider.models`; `integration_views` aggregates across multiple apps.
- Do not assume the `roadmap_pivot` directory is a standalone app — it only contains `templatetags/` and is not in `INSTALLED_APPS` directly.

---

## Tone & Collaboration

This is a production system used by real researchers and HPC resource providers. Changes have real-world impact on infrastructure visibility and compliance tracking.

- Ask clarifying questions rather than guessing intent.
- If a request is ambiguous about scope (e.g. "update the resource model"), ask which specific model field and in which app before proceeding.
- When something looks wrong (e.g. a missing FK constraint, an overly broad `import *`), flag it as an observation — don't silently fix it unless asked.
- Keep plans short and numbered. Long prose plans are harder to approve step-by-step.
- One migration per logical change. Never bundle unrelated model changes in a single migration.
