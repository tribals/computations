FROM python:3.8-slim AS builder

ARG app=/app

WORKDIR ${app}

ENV build_deps build-essential libpq-dev git

RUN set -ex; \
    apt-get update; \
    apt-get install -y --no-install-recommends --no-install-suggests ${build_deps};

COPY dist/computations-*-py3-none-any.whl ${app}/

RUN set -ex; \
    pip install --user computations-*-py3-none-any.whl

# ---

FROM python:3.8-slim

ARG app=/app

WORKDIR ${app}

ENV deps libpq5

RUN set -ex; \
    apt-get update; \
    apt-get install -y --no-install-recommends --no-install-suggests ${deps}; \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /usr/local/
COPY migrations ${app}/migrations/
COPY alembic.ini entrypoint.sh ${app}/

EXPOSE 8080

ENTRYPOINT ["./entrypoint.sh"]
