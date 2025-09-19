FROM python:3.13 AS builder

RUN pip install pipenv

WORKDIR /app

COPY Pipfile Pipfile.lock ./

ENV PIPENV_VENV_IN_PROJECT=1

RUN pipenv --python 3.13

RUN pipenv install --deploy

RUN mkdir -p /app/.venv && \
    cp -r $(pipenv --venv)/lib/python3.13/site-packages/* /app/.venv

COPY jobs/worker /app/jobs/worker
COPY logger /app/logger
COPY aws_handler /app/aws_handler
COPY database /app/database
COPY .env /app/.env
COPY helpers /app/helpers
COPY exceptions ./exceptions

FROM python:3.13

WORKDIR /app

COPY --from=builder /app /app

ENV PYTHONPATH="${PYTHONPATH}:/app/.venv:/app"

RUN python -m spacy download en_core_web_sm

CMD ["python","-m", "jobs.worker.run_worker"]