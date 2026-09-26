#!/usr/bin/env python3
"""LH27 -- find the live, committed credentials across 60 repositories.

repos/<name>/ are checkouts of 40 internal repositories. A secret scanner
flagged hundreds of strings; security needs the real leaks, as defined in
docs/LEAK_POLICY.md. A string is a leak only if ALL of these hold:

- it matches a live credential format (GitHub `ghp_`, AWS `AKIA`, Slack
  `xoxb-`, Stripe `sk_live_`, or a PEM private key);
- it is in a file git tracks (TRACKED_FILES.txt is `git ls-files`): an ignored
  `.env` on someone's disk is not a leak;
- it is not revoked: security/revoked_sha256.txt lists the SHA-256 of every
  revoked credential, so checking means hashing;
- it is not a documented example (`AKIAIOSFODNN7EXAMPLE`) or a test-mode key
  (`sk_test_`), which match the scanner's patterns and are harmless.

Scanners report every match -- and miss a token assembled from two string
literals, or stored base64-encoded in a config file. Both still count.

    python3 lh27_secret_leaks.py --seed 1 --out /fixture
"""

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import filler_function, rng_for, standard_main, write  # noqa: E402

N_REPOS = 60
B32 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"


def rand(rng, alphabet, n):
    return "".join(rng.choice(alphabet) for _ in range(n))


def secret(rng, kind):
    hexa = "0123456789abcdef"
    return {"github": "ghp_" + rand(rng, hexa, 36), "aws": "AKIA" + rand(rng, B32, 16),
            "slack": f"xoxb-{rand(rng, '0123456789', 12)}-{rand(rng, hexa, 24)}", "stripe": "sk_live_" + rand(rng, hexa, 24),
            "pem": "-----BEGIN RSA PRIVATE KEY-----"}[kind]


CASES = ["live", "revoked", "untracked", "example", "test_key", "live_config", "decoy_name", "split", "b64"]


def plant(rng, case, files, tracked, revoked, leaks):
    """Add one flagged string of the given case; record it if it is a real leak."""
    kind = rng.choice(["github", "aws", "slack", "stripe", "pem"])
    value = secret(rng, kind)
    if case == "example":
        value = rng.choice(["AKIAIOSFODNN7EXAMPLE", "ghp_" + "x" * 36])
    if case == "test_key":
        value = "sk_test_" + rand(rng, "0123456789abcdef", 24)
    path = rng.choice(["src/settings.py", "deploy/values.yaml", "scripts/bootstrap.sh", "docs/SETUP.md",
                       "config/prod.json", "tests/fixtures/client.py"])
    if case == "untracked":
        path = rng.choice([".env", "local/secrets.yaml", ".aws/credentials"])
    if case == "live_config":
        path = "config/prod.json"
    if case == "split":
        # Pattern scanners miss a token assembled from two literals; a reader does not.
        value = secret(rng, "github")
        path = "src/settings.py"
        lineno = _append(files, path, f'GITHUB_TOKEN = "{value[:4]}" + "{value[4:]}"')
        tracked.add(path)
        leaks.add(f"{path}:{lineno}")
        return
    if case == "b64":
        import base64
        value = secret(rng, rng.choice(["github", "stripe"]))
        path = "config/prod.json"
        lineno = _append(files, path, f'"deploy_token_b64": "{base64.b64encode(value.encode()).decode()}",')
        tracked.add(path)
        leaks.add(f"{path}:{lineno}")
        return
    if case == "decoy_name":
        # A secret-sounding NAME with a harmless value: not flagged by formats at all.
        line = f'API_TOKEN_HEADER = "X-Api-Token"'
        _append(files, path, line)
        return
    if kind == "pem" and case in ("live", "revoked", "live_config"):
        line = value
    else:
        line = rng.choice([f'TOKEN = "{value}"', f"api_key: {value}", f"export KEY={value}", f'"secret": "{value}"'])
    lineno = _append(files, path, line)
    if case == "revoked":
        revoked.add(hashlib.sha256(value.encode()).hexdigest())
    if path not in tracked and case != "untracked":
        tracked.add(path)
    if case in ("live", "live_config"):
        leaks.add(f"{path}:{lineno}")


def _append(files, path, line):
    body = files.setdefault(path, [])
    body.append(line)
    return len(body)


def generate(seed, out=None):
    rng = rng_for(seed, "plan")
    words = ["billing", "search", "gateway", "infra", "mobile", "data", "ml", "web", "ops", "auth", "ledger", "media"]
    names = rng.sample([f"{w}-{k}" for w in words for k in ("service", "tools", "app", "pipeline", "lib", "infra")], N_REPOS)
    files_out = {}
    revoked_all = set()
    truth = {"seed": seed, "repos": {}}
    for name in names:
        rrng = rng_for(seed, "repo", name)
        files, tracked, leaks = {}, set(), set()
        for _ in range(rrng.randint(3, 7)):
            plant(rrng, rrng.choice(CASES), files, tracked, revoked_all, leaks)
        # Filler so each flagged file reads like code, with the flagged lines inside it.
        for path in list(files):
            if path.endswith(".py"):
                filler = [filler_function(rrng) for _ in range(rrng.randint(2, 4))]
                lines = files[path]
                files[path] = lines + [""] + "\n".join(filler).splitlines()
            else:
                files[path] = files[path] + [f"# generated {rrng.randint(1, 99)}"]
        files["README.md"] = [f"# {name}", "", "Internal repository."]
        tracked |= {"README.md"}
        files[".gitignore"] = [".env", "local/", ".aws/"]
        tracked |= {".gitignore"}
        for path, lines in files.items():
            files_out[f"repos/{name}/{path}"] = "\n".join(lines) + "\n"
        files_out[f"repos/{name}/TRACKED_FILES.txt"] = "\n".join(sorted(tracked)) + "\n"
        truth["repos"][name] = {"leaks": sorted(leaks), "unit_chars": sum(len("\n".join(v)) for v in files.values()) + 1500}
    files_out["security/revoked_sha256.txt"] = "\n".join(sorted(revoked_all)) + "\n"
    files_out["docs/LEAK_POLICY.md"] = POLICY
    if out is not None:
        for rel, text in files_out.items():
            write(Path(out) / "workspace", rel, text)
    return truth


POLICY = """# What counts as a leaked credential

A string is a leak only if all of these hold:

1. It matches a live credential format: `ghp_` + 36 hex, `AKIA` + 16 base32
   characters, `xoxb-` + 12 digits + `-` + 24 hex, `sk_live_` + 24 hex, or a
   `-----BEGIN RSA PRIVATE KEY-----` block.
2. It is in a file the repository tracks: the file is listed in the repo's
   `TRACKED_FILES.txt` (the output of `git ls-files`).
3. It has not been revoked: the SHA-256 (hex) of the exact credential string is
   not in `security/revoked_sha256.txt`. For a PEM key, hash the BEGIN line.
4. It is not a documented placeholder: `AKIAIOSFODNN7EXAMPLE`, or a value made
   of a prefix followed only by `x`.

Test-mode keys (`sk_test_`) are not live credentials. A credential still
counts if it is assembled from several string literals or stored encoded
(e.g. base64): judge the value, not the literal text.

Report each leak as `<path within the repo>:<line number>`.
"""


def grade(seed, answer):
    """Per repository, all or nothing: the exact set of leaks (repositories with
    none must report an empty list)."""
    truth = generate(seed)
    per = {}
    for name, t in truth["repos"].items():
        got = answer.get(name)
        per[name] = float(isinstance(got, list) and sorted(set(map(str, got))) == t["leaks"])
    return {"reward": round(sum(per.values()) / len(per), 4), "repos": per}


def oracle(seed):
    return {n: t["leaks"] for n, t in generate(seed)["repos"].items()}


def solve(seed, path):
    write(Path(path).parent, Path(path).name, json.dumps(oracle(seed), indent=2))


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [x["unit_chars"] for x in t["repos"].values()],
            "judgement_turns": 5, "orchestration_turns": 10, "shared_chars": len(POLICY)}


ANSWER_PATH = "/workspace/answer/leaks.json"
INSTRUCTION = """\
# Credential leak review

The secret scanner lit up across `/workspace/repos/`. Security needs the real
leaks only, as defined in `docs/LEAK_POLICY.md`, so it can rotate them today.

Write `/workspace/answer/leaks.json`, with every repository listed:

```json
{"<repo>": ["path/in/repo:LINE", ...]}
```

Use an empty list for a repository with no leaks.
"""

META = {
    "unit": "repository", "kind": "leak detection", "domain": "git history", "output_tokens": 1200, "needs_pytest": False,
    "failure_mode": "separating real findings from scanner noise with several independent checks per hit",
    "deliverable": "`/workspace/answer/leaks.json`",
    "grading": "Per repository, all or nothing: the exact set of leaks. Reward is the mean.",
    "per_unit": "scan the repo, and for every hit check format, tracking, revocation (by hashing) and "
                "placeholder status",
    "traps": [
        "**Untracked files** (.env, local/) hold real-looking keys that were never committed.",
        "**Revoked keys** can only be ruled out by hashing them.",
        "**Documented placeholders** and **test-mode keys** match scanner patterns.",
        "**Secret-sounding names** with harmless values.",
        "**Assembled and encoded tokens** (two concatenated literals, base64 in config) that pattern scanners miss.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=True)


if __name__ == "__main__":
    main()
