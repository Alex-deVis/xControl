all: lint
.PHONY: lint install install-dev

lint:
	@autoflake --in-place  .
	@isort  .
	@black .

install:
	pip install -r pip-requirements.txt

install-dev:
	pip install -r pip-requirements-dev.txt
