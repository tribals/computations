#!/bin/sh

set -ex

case $1 in
    api)
        exec waitress-serve --call computations.http.api_v1:create_api
    ;;
    migrations)
		shift; exec alembic "$@"
	;;
    worker)
        shift; exec celery worker --app computations.worker:app "$@"
    ;;
esac

exec "$@"
