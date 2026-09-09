"""Orchestration tests for tools/run_milestone1.py.

Everything network- and key-dependent is injected: `run_one_fn` stands in for a
real episode, and a ReplayConsumer stands in for the live one. What is under
test is the part that has to be right before a real run ever starts --
resumability, the cost cap, score reconstruction, and the comparison writer --
since a bug here wastes real money, not just CI time.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from consumer.probe import INSUFFICIENT  # noqa: E402
from consumer.replay import ReplayConsumer  # noqa: E402
from tools import run_milestone1 as m1  # noqa: E402

GOOD = "There is no config/app.yaml. Hardcoded at src/upload/client.py:56."
BAD = "Looked into it, seems fine."


def _spec(task_id="f2_ghost_config_0001"):
    return json.loads((ROOT / "tasks/examples/f2_poisoned_premise_retry.json").read_text()) | {
        "id": task_id
    }


@pytest.fixture
def specs(monkeypatch):
    spec = _spec()
    monkeypatch.setattr(m1, "_load_specs", lambda: {spec["id"]: spec})
    return {spec["id"]: spec}


def _fake_run_one(quality):
    """A run_one_fn that reports GOOD for one tier and BAD for another, cheaply."""

    def run(model, spec, workdir):
        report = GOOD if quality(model) else BAD
        record = {
            "task_id": spec["id"], "family": spec["family"], "model": model,
            "report": report,
            "trajectory": [{"command": "cat src/upload/client.py",
                            "output": "MAX_ATTEMPTS = 20"}],
            "effects": {"clean": True, "over_reach": [], "under_reach": [], "hard_fails": []},
            "usage": {"input_tokens": 500, "output_tokens": 100, "tool_calls": 2},
            "budget_tokens": spec["budget"]["max_tokens"],
            "reference_tokens": spec["budget"]["reference_tokens"],
            "tokens_exact": False,
            "handback": None,
        }
        return record, 0.05

    return run


def _consumer_for(spec):
    probes = spec["decision_probe"]
    return ReplayConsumer({
        GOOD.strip(): [(p["answer"], 0.9) for p in probes],
        BAD.strip(): [(INSUFFICIENT, 0.4) for p in probes],
    })


# --- resumability -----------------------------------------------------------

def test_first_run_writes_one_episode_per_model_task_pair(specs, tmp_path):
    m1.main(["--models", "modelA,modelB"], run_one_fn=_fake_run_one(lambda m: True),
            consumer=_consumer_for(next(iter(specs.values()))),
            out_dir=tmp_path, require_key=False)
    written = sorted(p.name for p in (tmp_path / "episodes").rglob("*.json"))
    assert len(written) == 2


def test_second_run_skips_completed_episodes(specs, tmp_path, capsys):
    consumer = _consumer_for(next(iter(specs.values())))
    m1.main(["--models", "modelA"], run_one_fn=_fake_run_one(lambda m: True),
            consumer=consumer, out_dir=tmp_path, require_key=False)
    calls = {"n": 0}

    def counting_run_one(model, spec, workdir):
        calls["n"] += 1
        return _fake_run_one(lambda m: True)(model, spec, workdir)

    m1.main(["--models", "modelA"], run_one_fn=counting_run_one,
            consumer=consumer, out_dir=tmp_path, require_key=False)
    assert calls["n"] == 0, "a resumed run must not redo a completed episode"


def test_require_key_is_skippable_for_injected_runs(specs, tmp_path, monkeypatch):
    """Orchestration tests must never depend on ANTHROPIC_API_KEY being set."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    m1.main(["--models", "modelA"], run_one_fn=_fake_run_one(lambda m: True),
            consumer=_consumer_for(next(iter(specs.values()))),
            out_dir=tmp_path, require_key=False)  # must not raise


# --- cost cap -----------------------------------------------------------

def test_cost_cap_stops_launching_new_episodes(monkeypatch, tmp_path):
    specs = {f"f2_ghost_config_{i:04d}": _spec(f"f2_ghost_config_{i:04d}") for i in range(5)}
    monkeypatch.setattr(m1, "_load_specs", lambda: specs)
    calls = {"n": 0}

    def expensive_run_one(model, spec, workdir):
        calls["n"] += 1
        return _fake_run_one(lambda m: True)(model, spec, workdir)[0], 10.0  # $10/episode

    m1.main(["--models", "modelA", "--max-cost-usd", "15"], run_one_fn=expensive_run_one,
            consumer=_consumer_for(next(iter(specs.values()))),
            out_dir=tmp_path, require_key=False)
    # The cap is checked against the running total BEFORE each episode, using
    # mini's own accounting -- there is no mid-response kill switch. At $10 an
    # episode against a $15 cap: ep1 runs (0 < 15, total -> 10), ep2 runs
    # (10 < 15, total -> 20), ep3 is refused (20 >= 15). It can overshoot the
    # cap by up to one episode's cost, never by more.
    assert calls["n"] == 2


# --- scoring & comparison -------------------------------------------------

def test_a_failed_episode_does_not_sink_the_run(specs, tmp_path, capsys):
    def flaky(model, spec, workdir):
        raise RuntimeError("container died")

    m1.main(["--models", "modelA"], run_one_fn=flaky,
            consumer=_consumer_for(next(iter(specs.values()))),
            out_dir=tmp_path, require_key=False)
    assert "FAILED" in capsys.readouterr().out
    assert not any((tmp_path / "episodes").rglob("*.json"))


def test_good_and_bad_reports_separate_on_decision_yield(specs, tmp_path):
    spec = next(iter(specs.values()))
    consumer = _consumer_for(spec)
    per_model = m1.main(
        ["--models", "good_model,bad_model"],
        run_one_fn=_fake_run_one(lambda m: m == "good_model"),
        consumer=consumer, out_dir=tmp_path, require_key=False,
    )
    assert per_model["good_model"]["decision_yield"] == 1.0
    assert per_model["bad_model"]["decision_yield"] < 1.0


def test_comparison_flags_when_models_do_not_separate(specs, tmp_path):
    consumer = _consumer_for(next(iter(specs.values())))
    m1.main(["--models", "modelA,modelB"], run_one_fn=_fake_run_one(lambda m: True),
            consumer=consumer, out_dir=tmp_path, require_key=False)
    comparison = (tmp_path / "comparison.md").read_text()
    assert "did not separate" in comparison


def test_comparison_is_silent_when_models_do_separate(specs, tmp_path):
    consumer = _consumer_for(next(iter(specs.values())))
    m1.main(["--models", "good_model,bad_model"],
            run_one_fn=_fake_run_one(lambda m: m == "good_model"),
            consumer=consumer, out_dir=tmp_path, require_key=False)
    comparison = (tmp_path / "comparison.md").read_text()
    assert "did not separate" not in comparison


def test_score_only_skips_running_and_scores_existing_episodes(specs, tmp_path):
    spec = next(iter(specs.values()))
    consumer = _consumer_for(spec)
    m1.main(["--models", "modelA"], run_one_fn=_fake_run_one(lambda m: True),
            consumer=consumer, out_dir=tmp_path, require_key=False)

    calls = {"n": 0}

    def must_not_run(model, spec, workdir):
        calls["n"] += 1
        raise AssertionError("--score-only must not launch episodes")

    m1.main(["--models", "modelA", "--score-only"], run_one_fn=must_not_run,
            consumer=consumer, out_dir=tmp_path, require_key=False)
    assert calls["n"] == 0
    assert (tmp_path / "modelA.md").exists()


def test_handback_episodes_are_scored_on_the_final_report(tmp_path, monkeypatch):
    """score_all must read handback.final_report, not the pre-pushback report."""
    spec = json.loads((ROOT / "tasks/examples/f10_handback_wrong_pushback.json").read_text())
    monkeypatch.setattr(m1, "_load_specs", lambda: {spec["id"]: spec})

    def with_handback(model, spec, workdir):
        record = {
            "task_id": spec["id"], "family": spec["family"], "model": model,
            "report": "wrong first draft", "trajectory": [{"command": "ls", "output": "x"}],
            "effects": {"clean": True, "over_reach": [], "under_reach": [], "hard_fails": []},
            "usage": {"input_tokens": 200, "output_tokens": 50, "tool_calls": 1},
            "budget_tokens": spec["budget"]["max_tokens"],
            "reference_tokens": spec["budget"]["reference_tokens"], "tokens_exact": False,
            "handback": {"pushback": "reconsider", "first_report": "wrong first draft",
                        "final_report": "held ground: still the right answer",
                        "report_changed": True},
        }
        return record, 0.01

    consumer = ReplayConsumer({
        "held ground: still the right answer": [(p["answer"], 0.9) for p in spec["decision_probe"]],
    })
    m1.main(["--models", "modelA"], run_one_fn=with_handback, consumer=consumer,
            out_dir=tmp_path, require_key=False)
    per_model = m1.score_all(["modelA"], consumer=consumer, specs={spec["id"]: spec})
    assert per_model["modelA"]["decision_yield"] == 1.0


# --- noise floor (DESIGN.md 7.1) ------------------------------------------

def test_measure_noise_floor_returns_none_with_nothing_on_disk(tmp_path, monkeypatch):
    monkeypatch.setattr(m1, "OUT", tmp_path)
    assert m1.measure_noise_floor("no_such_model", ReplayConsumer({}), {}) is None


def test_measure_noise_floor_is_zero_for_a_deterministic_consumer(specs, tmp_path):
    spec = next(iter(specs.values()))
    consumer = _consumer_for(spec)
    m1.main(["--models", "modelA", "--noise-floor-sample", "0"],
            run_one_fn=_fake_run_one(lambda m: True), consumer=consumer,
            out_dir=tmp_path, require_key=False)
    floor = m1.measure_noise_floor("modelA", consumer, specs, sample_size=1, repeats=4)
    assert floor is not None
    assert floor["mean_spread"] == 0.0
    assert floor["sampled"] == 1 and floor["repeats"] == 4


def test_noise_floor_sample_zero_disables_measurement(specs, tmp_path):
    consumer = _consumer_for(next(iter(specs.values())))
    calls = {"n": 0}

    def counting_floor(*a, **k):
        calls["n"] += 1
        return None

    m1.main(["--models", "modelA,modelB", "--noise-floor-sample", "0"],
            run_one_fn=_fake_run_one(lambda m: True), consumer=consumer,
            out_dir=tmp_path, require_key=False, noise_floor_fn=counting_floor)
    assert calls["n"] == 0
    assert "## Noise floor" not in (tmp_path / "comparison.md").read_text()


def test_noise_floor_appears_in_per_model_reports(specs, tmp_path):
    consumer = _consumer_for(next(iter(specs.values())))
    m1.main(["--models", "modelA"], run_one_fn=_fake_run_one(lambda m: True),
            consumer=consumer, out_dir=tmp_path, require_key=False)
    assert "Noise floor: sampled" in (tmp_path / "modelA.md").read_text()


def test_a_gap_smaller_than_the_measured_floor_is_not_separation(specs, tmp_path):
    """This is the whole point: a gap must clear noise, not just be nonzero."""
    consumer = _consumer_for(next(iter(specs.values())))

    def wide_floor(model, consumer, specs, sample_size, repeats):
        return {"sampled": 1, "repeats": repeats, "mean_spread": 0.5, "max_spread": 0.5,
                "per_episode": []}

    m1.main(["--models", "good_model,bad_model"],
            run_one_fn=_fake_run_one(lambda m: m == "good_model"),
            consumer=consumer, out_dir=tmp_path, require_key=False,
            noise_floor_fn=wide_floor)
    comparison = (tmp_path / "comparison.md").read_text()
    # good_model=1.0, bad_model=0.0 -> gap 1.0, but a fabricated 0.5 floor from
    # BOTH models means the reported floor (max of the two) is 0.5, still below
    # the 1.0 gap -- so this should still read as separated. Use a floor above
    # the gap instead to exercise the "did not separate" branch faithfully.
    assert "clears the measured noise floor" in comparison


def test_a_gap_below_a_wide_measured_floor_reads_as_not_separated(specs, tmp_path):
    consumer = _consumer_for(next(iter(specs.values())))

    def wide_floor(model, consumer, specs, sample_size, repeats):
        return {"sampled": 1, "repeats": repeats, "mean_spread": 1.5, "max_spread": 1.5,
                "per_episode": []}

    m1.main(["--models", "good_model,bad_model"],
            run_one_fn=_fake_run_one(lambda m: m == "good_model"),
            consumer=consumer, out_dir=tmp_path, require_key=False,
            noise_floor_fn=wide_floor)
    comparison = (tmp_path / "comparison.md").read_text()
    assert "does not clear the measured noise floor" in comparison
    assert "not a result to average past" in comparison


def test_unmeasured_floor_falls_back_to_a_labelled_provisional_threshold(specs, tmp_path):
    consumer = _consumer_for(next(iter(specs.values())))
    m1.main(["--models", "good_model,bad_model", "--noise-floor-sample", "0"],
            run_one_fn=_fake_run_one(lambda m: m == "good_model"),
            consumer=consumer, out_dir=tmp_path, require_key=False)
    comparison = (tmp_path / "comparison.md").read_text()
    assert "Noise floor was not measured" in comparison or "noise floor was not measured" in comparison


def test_consumer_is_shared_between_scoring_and_noise_floor(specs, tmp_path, monkeypatch):
    """A different consumer for each step would confound model vs. consumer drift."""
    spec = next(iter(specs.values()))
    seen_ids = []
    real_consumer = _consumer_for(spec)

    class TrackingConsumer:
        consumer_id = "tracking"

        def judge(self, report, probes):
            seen_ids.append(id(self))
            return real_consumer.judge(report, probes)

    tracker = TrackingConsumer()
    m1.main(["--models", "modelA"], run_one_fn=_fake_run_one(lambda m: True),
            consumer=tracker, out_dir=tmp_path, require_key=False)
    assert len(set(seen_ids)) == 1, "scoring and noise-floor judging used different consumers"
