FROM python:3.13 AS builder

RUN pip install pipenv

WORKDIR /app

COPY Pipfile Pipfile.lock ./

ENV PIPENV_VENV_IN_PROJECT=1

RUN pipenv --python 3.13

RUN pipenv install --deploy

RUN mkdir -p /app/.venv && \
    cp -r $(pipenv --venv)/lib/python3.13/site-packages/* /app/.venv

COPY logger /app/logger
COPY database /app/database
COPY .env /app/.env
COPY helpers /app/helpers
COPY exceptions ./exceptions
COPY api ./api
COPY cache /app/cache

FROM python:3.13

WORKDIR /app

COPY --from=builder /app /app

ENV PYTHONPATH="${PYTHONPATH}:/app/.venv:/app"


CMD ["python", "-m", "fastapi", "run", "./api/tracker_api.py"]