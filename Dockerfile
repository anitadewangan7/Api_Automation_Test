# 1. Build Stage
FROM python:3.9-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# 2. Runtime Stage
FROM python:3.9-slim

WORKDIR /app
# Copy installed dependencies from the builder
COPY --from=builder /root/.local /root/.local
COPY . .

# Ensure local bin is in PATH
ENV PATH=/root/.local/bin:$PATH

# By default, we run tests. 
# We don't bake credentials into the image; we inject them at runtime.
CMD ["pytest"]