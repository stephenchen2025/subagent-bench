.PHONY: help test validate fixture-tests

help: ## Show available targets
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Install development requirements
	python -m pip install -r requirements-dev.txt

test: ## Validate task specs and fixture invariants
	python -m pytest tests -q

fixture-tests: ## Run the fixture repo's own test suite (3 failures are planted bait)
	cd envs/py_svc/repo && python -m pytest tests -q || true
