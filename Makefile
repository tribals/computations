MAKEFLAGS += --no-builtin-rules

.SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c

# tools
packager = poetry

format = black
format_imports = isort
lint = pyflakes
test = pytest

# paths
pkg = computations
tests = tests
migrations = migrations

sources_packaging = \
	pyproject.toml \
	poetry.lock

sources_pkg = \
	$(pkg)/*.py \
	$(pkg)/http/*.py \
	$(pkg)/http/schemas/*.py

sources_pkg_data = \
	$(pkg)/http/schemas/*.json

sources_tests = \
	$(tests)/*.py \
	$(tests)/http/*.py

sources_migrations = \
	$(migrations)/*.py \
	$(migrations)/versions/*.py

sources_py = \
	$(sources_pkg) \
	$(sources_tests) \
	$(sources_migrations)

sources_all = \
	$(sources_packaging) \
	$(sources_pkg) \
	$(sources_pkg_data) \
	$(sources_tests) \
	$(sources_migrations)

# other
version = $(word 2, $(shell $(packager) version))

.PHONY: test
test:
	@echo $(version)
	@echo $(sources_py)

dist/$(pkg)-*-py3-none-any.whl: $(sources_packaging) $(sources_pkg) $(sources_pkg_data)
	$(packager) build --format wheel

.PHONY: clean
clean:
	rm -f dist/*
	rm -f .format .lint .test .test-full .check .check-full

.format: $(sources_py)
	$(packager) run $(format) $(pkg) $(tests) $(migrations)
	$(packager) run $(format_imports) $(pkg) $(tests) $(migrations)

	@touch .format


.lint: $(sources_py)
	$(packager) run $(lint)  $(pkg) $(tests) $(migrations)

	@touch .lint


.test: $(sources_py) .pytest_cache
	$(packager) run $(test) -m 'not integration'

	@touch .test


.test-full: $(sources_py) .pytest_cache .setup-db .setup-rabbitmq .docker-compose-up-one-werker
	$(packager) run $(test)

	@touch .test-full


.check: .format .lint .test
	@touch .check


.check-full: .format .lint .test-full
	@touch .check-full


.docker-compose-build: dist/$(pkg)-*-py3-none-any.whl
	docker-compose build

	@touch .docker-compose-build


.docker-compose-up-deps: .docker-compose-build
	docker-compose up --detach postgres rabbitmq

	@touch .docker-compose-up-deps


.docker-compose-up-one-werker: .docker-compose-up-deps
	docker-compose up --detach worker-machine1

	@touch .docker-compose-up-one-werker


.setup-db: .docker-compose-up-deps
	docker-compose run api migrations upgrade head

	@touch .setup-db


.setup-rabbitmq: .docker-compose-up-deps
	docker-compose exec rabbitmq sh -c 'set -ex; \
rabbitmqctl add_vhost computations; \
rabbitmqctl add_user computations sesame; \
rabbitmqctl set_permissions --vhost computations computations ".*" ".*" ".*"'

	@touch .setup-rabbitmq

.docker-compose-up: .docker-compose-up-deps .setup-db .setup-rabbitmq
	docker-compose up --detach api worker-machine1 worker-machine2

	@touch .docker-compose-up

.PHONY: docker-compose-down
docker-compose-down:
	docker-compose down --volumes
	rm .docker-compose-* .setup-*
