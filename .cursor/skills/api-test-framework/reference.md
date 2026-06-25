# API Test Framework — Reference

## Directory structure

```
Api_Test_Framework/
├── .env                          # Local secrets (gitignored)
├── .gitignore
├── conftest.py                   # Session fixtures + pytest hooks
├── pytest.ini                    # Pytest defaults and markers
├── requirements.txt
├── Dockerfile
├── README.md
├── assets/style.css              # pytest-html report styling
├── .github/workflows/api-test.yml
├── .cursor/skills/api-test-framework/   # This skill
├── src/
│   ├── api_client.py             # BookerClient (SOM)
│   └── schemas/
│       └── booking_schema.json
└── tests/
    └── test_bookings.py
```

## File responsibilities

### `src/api_client.py`

`BookerClient` encapsulates all RESTful Booker HTTP interaction:

- `__init__`: loads `.env`, stores `base_url` and `auth`, calls `_get_token()`
- `_get_token()`: POST `/auth` with username/password
- `get_booking(id)`: GET `/booking/{id}`
- `create_booking(payload)`: POST `/booking` with JSON body

Extend this class for UPDATE, DELETE, and other endpoints.

### `conftest.py`

| Item | Purpose |
|------|---------|
| `client` fixture | Session-scoped `BookerClient` instance |
| `booking_schema` fixture | Loads `src/schemas/booking_schema.json` once |
| `pytest_metadata` hook | Adds project name/environment to HTML report |

### `src/schemas/booking_schema.json`

JSON Schema contract for booking GET response fields: `firstname`, `lastname`, `totalprice`, `depositpaid` (all required).

### `tests/test_bookings.py`

| Test / fixture | Behavior |
|----------------|----------|
| `created_booking` | Creates booking via POST, yields `bookingid`, optional teardown |
| `test_get_created_booking` | Positive GET: 200, latency, schema validation |
| `test_get_invalid_booking` | Negative GET: 404 for non-existent ID |
| `test_create_booking` | Parametrized POST: valid (200) and invalid (500) payloads |

### `pytest.ini`

Auto-applies: `--html=report.html --self-contained-html`, console logging, `testpaths = tests`, warning filters, smoke/regression markers.

### `requirements.txt`

`pytest`, `requests`, `jsonschema`, `python-dotenv`, `pytest-html`

### `.github/workflows/api-test.yml`

Triggers on push/PR to `main`/`develop`. Runs `pytest` with GitHub secrets, uploads `report.html` artifact, builds Docker image.

### `Dockerfile`

Multi-stage: builder installs deps, runtime copies app and runs `CMD ["pytest"]`.

## Test execution flow

```
pytest
  → pytest.ini applies addopts
  → conftest.py: BookerClient + schema fixtures (session)
  → test file fixtures (e.g. created_booking)
  → test assertions
  → report.html generated
```

## Dependencies between layers

```
.env ──► BookerClient ──► tests
              │
              └──► requests ──► RESTful Booker API

booking_schema.json ──► conftest fixture ──► jsonschema.validate in tests
```
