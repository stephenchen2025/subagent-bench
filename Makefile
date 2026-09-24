.PHONY: help test validate fixture-tests orch-generate orch-rehearse orch-validate orch-run

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

live-trial: ## Run one real trial + live consumer (needs ANTHROPIC_API_KEY; no Docker)
	python tools/live_trial.py $(TASK)

generate: ## Generate a Milestone-1 task set (30 tasks) into tasks/generated
	python tools/generate_tasks.py --per-family 10

dry-run: ## Rehearse the whole pipeline at Milestone-1 scale (no model, no key)
	python tools/dry_run.py

milestone1: ## Run Milestone 1 for real: both default models, resumable, cost-guarded
	python tools/run_milestone1.py

# --- orchestrator track (ORCHESTRATOR.md) -------------------------------------

orch-generate: ## Regenerate the checked-in task set, datasets/orch-v0.2
	python tools/orch_generate.py

orch-rehearse: ## Rehearse the orchestrator track with scripted policies (no model, no key; needs mini)
	python tools/orch_rehearse.py

orch-validate: ## Prove every task solvable: Harbor's oracle agent must score 1.0 (needs Docker)
	harbor run -p datasets/orch-v0.2 -a oracle -n 4 -o build/jobs-oracle -y

orch-run: ## Real run, no Docker: MODELS="anthropic/claude-haiku-4-5-20251001" (needs ANTHROPIC_API_KEY)
	python tools/orch_run.py --models $(MODELS)
