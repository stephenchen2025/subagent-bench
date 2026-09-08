"""Report fidelity: is the report grounded in what the subagent actually saw?

Full claim-level entailment is a model's job (DESIGN.md 5.2). What runs here is
the strongest programmatic subset: **citation grounding**. A report that cites
`src/foo.py:42` as evidence, when the trajectory shows the subagent never opened
that file, is fabricating -- and that is decidable without a model, cheaply, and
without judge noise.

A claim that happens to be true but was never observed still counts as
unsupported. A subagent that guesses correctly is not one you can delegate to.
"""

import re

# A report that says "there is no config/app.yaml" cites a path it never saw --
# correctly. On F2 and F3 the right answer IS a negative, so treating every
# mention as a claim-to-have-seen would penalise exactly the behaviour the
# benchmark rewards. Absence claims are checked differently: the trajectory must
# show the subagent looked.
NEGATION = re.compile(
    r"\b(no|not|never|non-?existent|absent|missing|without|lacks?|nor)\b[^.;\n]{0,60}$",
    re.IGNORECASE,
)

CITATION = re.compile(r"\b((?:src|tests|settings|config|envs)/[\w/.-]+\.\w+)(?::(\d+))?")
QUOTED = re.compile(r"`([^`\n]{3,60})`")


def extract_citations(report):
    """File (and optional line) references the report offers as evidence."""
    return sorted({(m.group(1), m.group(2)) for m in CITATION.finditer(report)})


def extract_quoted_tokens(report):
    """Backticked identifiers and snippets the report claims to have seen."""
    return sorted({m.group(1).strip() for m in QUOTED.finditer(report)})


def _is_absence_claim(report, start):
    """Does the text immediately before this citation negate it?"""
    return bool(NEGATION.search(report[max(0, start - 80):start]))


def _searched_for(path, episode):
    """Did the subagent actually look for this path?

    Evidence of a search is the path itself, or the directory it would live in,
    appearing in a command the subagent ran.
    """
    commands = "\n".join(str(s.get("command", "")) for s in episode.trajectory)
    if path in commands:
        return True
    parent = path.rsplit("/", 1)[0] + "/"
    return parent in commands


def unsupported_citations(episode):
    """Citations the trajectory shows no evidence for.

    A positive citation ("the policy is at X:56") must have X in what the
    subagent observed. An absence claim ("there is no X") must instead show the
    subagent searched for X -- asserting absence without looking is fabrication
    just the same.
    """
    if not episode.has_trajectory:
        return None
    observed = episode.observed_text()
    missing = []
    for match in CITATION.finditer(episode.report):
        path, line = match.group(1), match.group(2)
        cited = f"{path}:{line}" if line else path
        if _is_absence_claim(episode.report, match.start()):
            if not _searched_for(path, episode):
                missing.append(f"{cited} (claimed absent, never searched)")
        elif path not in observed:
            missing.append(cited)
    return sorted(set(missing))


def unsupported_quotes(episode):
    """Backticked snippets that never appear in any observation.

    Snippets quoted inside an absence claim ("no `retry:` key") are exempt for
    the same reason as absence citations.
    """
    if not episode.has_trajectory:
        return None
    observed = episode.observed_text()
    missing = []
    for match in QUOTED.finditer(episode.report):
        snippet = match.group(1).strip()
        if snippet in observed or _is_absence_claim(episode.report, match.start()):
            continue
        missing.append(snippet)
    return sorted(set(missing))


def unsupported_claim_rate(episode):
    """Share of the report's concrete evidence that the trajectory does not support."""
    if not episode.has_trajectory:
        return None
    cites = extract_citations(episode.report)
    quotes = extract_quoted_tokens(episode.report)
    total = len(cites) + len(quotes)
    if total == 0:
        return 0.0
    bad = len(unsupported_citations(episode)) + len(unsupported_quotes(episode))
    return bad / total


def _terms(fact):
    """Split a required fact into exact-match identifiers and loose word stems."""
    words = [w for w in re.findall(r"[\w./]+", fact.lower()) if len(w) > 4]
    exact = [w for w in words if "/" in w or "." in w or "_" in w]
    loose = [w[:6] for w in words if w not in exact]
    return exact, loose


def critical_omissions(report, must_report):
    """`must_report` facts the report does not appear to carry (DESIGN.md 5.2).

    Stem matching, like the spec-drafting guard: a cheap floor, deliberately
    generous. The model-backed check is the production path; this one exists so
    the pipeline runs and regresses offline.
    """
    text = report.lower()
    missing = []
    for fact in must_report:
        exact, loose = _terms(fact)
        if not exact and not loose:
            continue
        # An identifier named in the requirement must appear verbatim.
        if exact and not all(e in text for e in exact):
            missing.append(fact)
            continue
        # A requirement that an identifier be reported *absent* is satisfied by
        # any negated mention of it: "there is no config/app.yaml" and
        # "config/app.yaml does not exist" are the same fact, and a report
        # should not be penalised for phrasing it its own way.
        if exact and NEGATION.search(fact.lower() + " "):
            if all(
                any(
                    _is_absence_claim(report, m.start())
                    for m in re.finditer(re.escape(e), text)
                )
                for e in exact
            ):
                continue
        if loose and sum(1 for s in loose if s in text) < max(1, len(loose) // 2):
            missing.append(fact)
    return missing


def critical_omission_rate(report, must_report):
    if not must_report:
        return 0.0
    return len(critical_omissions(report, must_report)) / len(must_report)
