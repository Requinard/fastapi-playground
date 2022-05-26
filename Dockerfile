FROM python:3-bullseye
WORKDIR /app
RUN pip install poetry
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

COPY . .
RUN ls -l
CMD ["uvicorn", "playground.main:app", "--host", "0.0.0.0", "--port", "8000"]

