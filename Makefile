SOURCES = computations tests migrations

EXEC = poetry run

FORMAT = black
FORMAT_IMPORTS = isort

LINT = pyflakes

TEST = pytest


.PHONY: format
format:
	$(EXEC) $(FORMAT) $(SOURCES)
	$(EXEC) $(FORMAT_IMPORTS) $(SOURCES)


.PHONY: lint
lint:
	$(EXEC) $(LINT) $(SOURCES)


.PHONY: test
test:
	$(EXEC) $(TEST)


.PHONY: check
check: format lint test


.PHONY: setup-rabbitmq
setup-rabbitmq:
	docker-compose exec rabbitmq sh -c 'set -ex; \
rabbitmqctl add_vhost computations; \
rabbitmqctl add_user computations sesame; \
rabbitmqctl set_permissions --vhost computations computations ".*" ".*" ".*"'
