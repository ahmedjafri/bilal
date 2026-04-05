FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./
RUN poetry install --only main --no-interaction

COPY src/ src/

EXPOSE 8080

CMD ["bilal"]
