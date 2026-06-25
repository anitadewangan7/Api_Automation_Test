---
name: api-test-framework
description: >-
  Guides development and testing for the RESTful Booker API automation framework
  (Python, Pytest, Service Object Model). Use when adding API client methods,
  writing or updating tests, JSON schemas, fixtures, CI/CD config, running pytest,
  debugging test failures, or explaining this project's structure and conventions.
---

# RESTful Booker API Test Framework

## Quick context

Python + Pytest API automation targeting [RESTful Booker](https://restful-booker.herokuapp.com).

| Layer | Location | Responsibility |
|-------|----------|------------------|
| Config | `.env`, `pytest.ini` | URLs, credentials, pytest defaults |
| API client (SOM) | `src/api_client.py` | HTTP calls, auth, logging |
| Schemas | `src/schemas/` | JSON contract validation |
| Fixtures | `conftest.py`, test files | Shared setup/teardown |
| Tests | `tests/` | Business scenarios and assertions |
| CI/CD | `.github/workflows/api-test.yml`, `Dockerfile` | Automated runs |

**Pattern:** Service Object Model — all API logic stays in `BookerClient`; tests only describe *what* to verify.

## Before making changes

1. Read `src/api_client.py`, relevant test file, and `conftest.py`.
2. Match existing naming, logging, and `requests` usage.
3. Never hardcode credentials or `BASE_URL` — use `.env` via `python-dotenv`.
4. Keep changes minimal; do not refactor unrelated code.

## Environment setup

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` in project root (not committed):

```
BASE_URL=https://restful-booker.herokuapp.com
USERNAME=admin
PASSWORD=password123
```

## Run tests

```bash
# Full suite (pytest.ini auto-generates report.html)
pytest

# Single file or test
pytest tests/test_bookings.py
pytest tests/test_bookings.py::test_get_invalid_booking

# With markers (defined in pytest.ini)
pytest -m smoke
```

Open `report.html` in a browser after a run. Logs print to console (`log_cli = true` in `pytest.ini`).

**Docker:**

```bash
docker build -t api-test-framework .
docker run --env-file .env api-test-framework
```

## Workflows

### Add a new API client method

1. Add method to `BookerClient` in `src/api_client.py`.
2. Build URL from `self.base_url`.
3. Use `requests` with appropriate verb; set headers when required (POST needs `Content-Type: application/json`).
4. Log request URL, status, and body (follow `get_booking` / `create_booking` pattern).
5. Return the raw `response` object (tests assert on it).

```python
def delete_booking(self, booking_id):
    url = f"{self.base_url}/booking/{booking_id}"
    headers = {"Cookie": f"token={self.token}"}
    response = requests.delete(url, headers=headers)
    logger.info(f"DELETE Request: {url} | Status: {response.status_code}")
    return response
```

### Add a new test

1. Add test function in `tests/test_*.py` (must start with `test_`).
2. Inject fixtures by name: `client`, `booking_schema`, or local fixtures.
3. Assert status code first, then body/schema/performance as needed.
4. Use `@pytest.mark.parametrize` for multiple data sets on one scenario.
5. Use fixtures with `yield` for setup/teardown (see `created_booking` in `test_bookings.py`).

**Validation checklist for GET responses:**

- `assert response.status_code == <expected>`
- `assert response.elapsed.total_seconds() < 2.0` (SLA check, when relevant)
- `validate(instance=response.json(), schema=booking_schema)` (contract test)

### Add or update a JSON schema

1. Create or edit `src/schemas/<name>_schema.json`.
2. Load via a session-scoped fixture in `conftest.py` (follow `booking_schema` pattern).
3. Validate in tests with `jsonschema.validate`.

### Add a shared fixture

- **Session scope** (`scope="session"`): expensive setup used by many tests — e.g. `client`, schemas. Put in `conftest.py`.
- **Function scope** (default): per-test data — e.g. `created_booking`. Put in test file or `conftest.py` if reused across files.

### Update CI/CD

- GitHub Actions: `.github/workflows/api-test.yml` — secrets `BASE_URL`, `USERNAME`, `PASSWORD` must exist in repo settings.
- Dockerfile runs `pytest` by default; inject env at runtime, never bake credentials into the image.

## Conventions

| Topic | Convention |
|-------|------------|
| Test files | `tests/test_*.py` |
| Test functions | `test_<scenario>` |
| Client class | `BookerClient` in `src/api_client.py` |
| Imports in tests | `from jsonschema import validate`; fixtures injected, not imported |
| Auth | Token fetched in `__init__` via `_get_token()`; use cookie header for protected endpoints |
| Reports | `report.html` via `pytest-html` (configured in `pytest.ini`) |
| Markers | `@pytest.mark.smoke`, `@pytest.mark.regression` |

## Existing test coverage

| ID | Scenario | Expected |
|----|----------|----------|
| TC01 | GET created booking | 200 + schema + latency < 2s |
| TC02 | GET invalid ID | 404 |
| TC03 | POST valid payload | 200 |
| TC04 | POST incomplete payload | 500 |

## Anti-patterns

- Putting URLs or auth logic directly in test files.
- Committing `.env`, `venv/`, or `report.html`.
- Asserting only status code when contract or field-level validation is required.
- Creating a new HTTP wrapper instead of extending `BookerClient`.

## Additional resources

- Architecture and file-by-file details: [reference.md](reference.md)
