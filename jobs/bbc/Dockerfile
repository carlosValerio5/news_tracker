FROM public.ecr.aws/lambda/python:3.13-x86_64 AS builder

# Copy requirements for dependency install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --target "/var/task"

FROM public.ecr.aws/lambda/python:3.13-x86_64

# Copy application code (adjust as needed for your dirs)
COPY jobs ./jobs
COPY aws_handler ./aws_handler
COPY database ./database

COPY jobs/bbc/lambda_handler.py ./lambda_handler.py
# Copy dependencies from builder
COPY --from=builder /var/task /var/task

# Set your Lambda handler (example: jobs.bbc.scraper.lambda_handler)
CMD ["lambda_handler.lambda_handler"]