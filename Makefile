.PHONY: format
format:
	uv run ruff format ./src ./tests
	uv run ruff check --fix --unsafe-fixes

.PHONY: lint
lint:
	uv run ruff format --diff
	uv run ruff check --exit-non-zero-on-fix 
	uv run flake8 ./src --select=WPS --count

.PHONY: types
types:
	uv run mypy ./src

.PHONY: ci
ci: lint types
