.PHONY: help test validate fixture-tests

help: ## Show available targets
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Install development requirements
	python -m pip install -r requirements-dev.txt

test: ## Validate task specs and fixture invariants
	python -m pytest tests -q

fixture-tests: ## Run the fixture repo's own test suite (3 failures are planted bait)
	cd envs/py_svc/repo && python -m pytest tests -q || true

demo: ## Score two subagents that did identical work but wrote different reports
	python tools/demo_scorecard.py

tasks: ## Emit Harbor task directories into build/harbor
	python tools/emit_harbor_tasks.py

test-harbor: ## Run the Harbor integration tests (needs Python >=3.12 + harbor from source)
	@echo "Harbor is not on PyPI and needs Python >=3.12. Set up once:"
	@echo "  git clone --depth 1 https://github.com/harbor-framework/harbor /tmp/harbor"
	@echo "  uv venv --python 3.12 /tmp/hv && uv pip install -p /tmp/hv/bin/python -e /tmp/harbor pytest jsonschema mini-swe-agent"
	/tmp/hv/bin/python -m pytest tests/test_harbor_integration.py -q
