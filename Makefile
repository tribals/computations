SOURCES = computations tests

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
