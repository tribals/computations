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


.test-full: $(sources_py) .pytest_cache
	$(packager) run $(test)

	@touch .test-full


.check: .format .lint .test
	@touch .check


.check-full: .format .lint .test-full
	@touch .check-full


.docker-compose-build: dist/$(pkg)-*-py3-none-any.whl
	docker-compose build

	@touch .docker-compose-build


.PHONY: docker-compose-up-deps
docker-compose-up-deps:
	docker-compose up --detach postgres rabbitmq


.PHONY: docker-compose-up-one-worker
docker-compose-up-one-worker:
	docker-compose up --detach worker-machine1


.PHONY: setup-db
setup-db:
	docker-compose run api migrations upgrade head


.PHONY: setup-rabbitmq
setup-rabbitmq:
	docker-compose exec rabbitmq sh -c 'set -ex; \
rabbitmqctl add_vhost computations; \
rabbitmqctl add_user computations sesame; \
rabbitmqctl set_permissions --vhost computations computations ".*" ".*" ".*"'


.PHONY: docker-compose-up
docker-compose-up:
	docker-compose up --detach


.PHONY: docker-compose-down
docker-compose-down:
	docker-compose down --volumes
