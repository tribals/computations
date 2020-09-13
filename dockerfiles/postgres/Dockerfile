FROM postgres:12.4-alpine

ENV POSTGRES_PASSWORD postgres

COPY init-user-db.sql /docker-entrypoint-initdb.d/
