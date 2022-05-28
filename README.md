# FastAPI Playground

A project where I make FastAPI do some cool stuff such as generic filtering, async database use and more.

It really takes the effort out of developing APIs.

## Interesting bits

These are some interesting takeaways to maybe copy and paste into your own projects.

File|What does it do
---|---
playground/providers/database.py|This module provides sync sessions for the database
playground/providers/database_async.py|This module provides async sessions to talk to the database
playground/providers/settings.py|Automatically read env vars and expose them to us with defaults
playground/routers/auditing.py|Automatically do auditing-related things with requests. Any request will have extra logging applied.
playground/routers/auth_passthrough.py|Create a HTTP client with a users credentials so we make requests on a users behalf.
playground/routers/health.py|Implement some extremely simple ready and live checks.
playground/routers/paginator.py|Paginate in-memory data in a re-usable manner.
playground/routers/time_range.py|Filter and request data from a database with filtering implemented in a re-usable manner.
tests/conftest.py|Creates pytest fixtures for the database, async database and a testclient. It can then be used in the tests without effort.
tests/mimesis.py|A small test case to test fake data with mimesis.
tests/mimesis.py|Run tests repeatedly and with parameterized instances.
tests/routers/test_*.py|Test API endpoints, backed by an in-memory SQLite database.
tests/test_schematesis.py|Automatically test the *entire* API from the spec without writing any cases!

## Why is FastAPI so neat

- It's a library, not a framework, making it easy to integrate it into any environment
- Hot reload that takes less than a second to restart
- Pydantic is used for data parsing, making it easy to describe datamodels
- OpenAPI spec is generated automatically from Pydantic models and FastAPI routes
- Open-ended dependency system that makes dependencies a breeze to manage
- Fully type annotated

## How to run it?

First make sure you have the following installed:

- python (3.10 or higher)
- poetry (https://python-poetry.org/). This tool installs dependencies and arranges virtual-envs

Now we can run the following

```shell
poetry install
poetry run uvicorn playground.main:app --reload --host 0.0.0.0 --port 8000
```

You can now open http://127.0.0.1:8000 in your browser. Uvicorn will automatically reload if you make any changes.

### What about docker?

Of course it runs in docker as well. Simply run `docker-compose up -d` to start it.


### What about code quality tools

```shell
poetry run pflake8 # Linting
poetry run mypy playground # Validate type annotations
poetry run pytest # Run unit and api tests
```
