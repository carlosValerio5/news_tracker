FROM public.ecr.aws/lambda/python:3.13-x86_64 AS builder

RUN pip install pipenv

WORKDIR /build

COPY Pipfile Pipfile.lock ./

RUN pipenv install --deploy

RUN mkdir -p /python && \
    cp -r $(pipenv --venv)/lib/python3.13/site-packages/* /python/

FROM public.ecr.aws/lambda/python:3.13-x86_64

COPY jobs/trends ./jobs/trends
COPY aws_handler ./aws_handler
COPY database ./database
COPY jobs/trends/lambda_handler.py ./lambda_handler.py
COPY logger ./logger

COPY --from=builder /python /var/task

CMD ["lambda_handler.lambda_handler"]