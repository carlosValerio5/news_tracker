# -------- Stage 1: Builder --------
FROM public.ecr.aws/lambda/python:3.13-x86_64 AS builder

# Install Pipenv and system dependencies
RUN pip install pipenv

# Set working directory
WORKDIR /build

# Copy Pipenv files
COPY Pipfile Pipfile.lock ./

# Install dependencies into a temporary virtualenv
RUN pipenv install --deploy

# Copy site-packages to a clean directory
RUN mkdir -p /python && \
    cp -r $(pipenv --venv)/lib/python3.13/site-packages/* /python/

# -------- Stage 2: Final --------
FROM public.ecr.aws/lambda/python:3.13-x86_64

# Copy application code
COPY jobs/bbc ./jobs/bbc
COPY aws_handler ./aws_handler
COPY database ./database
COPY jobs/bbc/lambda_handler.py ./lambda_handler.py

# Copy dependencies from builder
COPY --from=builder /python /var/task

# Set the handler (update this if your actual function is different)
CMD ["lambda_handler.lambda_handler"]
