#!/usr/bin/env python3
"""LH19 -- fix the accessibility failures on 48 pages of a marketing site.

site/pages/*.html fail an accessibility audit. docs/A11Y.md states six rules,
and each fix needs a fact that lives somewhere specific:

- A1 `<html lang>` -- the page's locale is in site/pages.json, not guessable;
- A2 image alt text -- decorative images (class `decorative`) get `alt=""`;
  informative ones get exactly their `data-description`;
- A3 form fields need a `<label for>` whose text is the field's `data-label`
  (and a field without an id gets its `name` as id);
- A4 headings may not skip levels -- fix the level, keep the text;
- A5 icon-only buttons need `aria-label` = their `data-action`;
- A6 vague link text ("click here", "read more", "here") is replaced by the
  link's `title`.

The grader parses every page, checks each rule, and checks that nothing else
changed: same text (apart from A6), same elements, same attributes.

    python3 lh19_a11y_fixes.py --seed 1 --out /fixture
"""

import json
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import filler_prose, rng_for, standard_main, write  # noqa: E402

N_PAGES = 48
LOCALES = ["en-GB", "de-DE", "fr-FR", "nl-NL", "es-ES", "pl-PL", "sv-SE", "it-IT"]
VAGUE = ["click here", "read more", "here"]


def model(rng, page):
    """A page as a list of blocks; render(fixed=...) produces broken or fixed HTML."""
    blocks = [("h", 1, page.replace("-", " ").title())]
    level = 1
    for _ in range(rng.randint(5, 9)):
        kind = rng.choice(["para", "img", "form", "button", "link", "heading", "heading"])
        if kind == "heading":
            # Sometimes skip a level (the broken page), always one deeper at most when fixed.
            jump = 2 if rng.random() < 0.35 and level <= 4 else rng.choice([0, 1]) if level < 5 else 0
            new = min(level + jump, 6)
            blocks.append(("h", new, rng.choice(["Overview", "Pricing", "How it works", "Details", "FAQ",
                                                "Our team", "Get started", "Security"])))
            level = new
        elif kind == "para":
            blocks.append(("p", filler_prose(rng, 1)))
        elif kind == "img":
            if rng.random() < 0.4:
                blocks.append(("img", "decorative", f"/img/divider-{rng.randint(1, 9)}.svg", None))
            else:
                blocks.append(("img", "photo", f"/img/{page}-{rng.randint(1, 99)}.jpg",
                               rng.choice(["Our support team at work", "The dashboard showing monthly usage",
                                           "A customer using the mobile app", "Chart of response times in 2026"])))
        elif kind == "form":
            fields = []
            for j in range(rng.randint(1, 3)):
                # Unique per page: two forms must never share an id.
                name = rng.choice(["email", "company", "phone", "country", "message", "size"]) + f"_{len(blocks)}{j}"
                fields.append((rng.choice(["input", "select", "textarea"]), name,
                               rng.choice(["Work email", "Company name", "Phone number", "Country", "Your message", "Team size"]),
                               rng.random() < 0.5))
            blocks.append(("form", fields))
        elif kind == "button":
            blocks.append(("button", rng.choice(["close-dialog", "open-menu", "play-video", "next-slide"])))
        else:
            blocks.append(("a", f"/docs/{page}/{rng.randint(1, 50)}", rng.choice(VAGUE),
                           rng.choice(["Read the pricing guide", "See the security whitepaper",
                                       "Open the API reference", "Compare plans"])))
    return blocks


def render(page, locale, blocks, fixed):
    lang = f' lang="{locale}"' if fixed else ""
    out = [f"<html{lang}>", "<head><title>" + page + "</title></head>", "<body>"]
    level = 0
    for b in blocks:
        if b[0] == "h":
            lvl = b[1]
            if fixed:
                lvl = min(lvl, level + 1)
            level = lvl
            out.append(f"<h{lvl}>{b[2]}</h{lvl}>")
        elif b[0] == "p":
            out.append(f"<p>{b[1]}</p>")
        elif b[0] == "img":
            _, kind, src, desc = b
            if kind == "decorative":
                out.append(f'<img class="decorative" src="{src}"' + (' alt=""' if fixed else "") + ">")
            else:
                out.append(f'<img src="{src}" data-description="{desc}"' + (f' alt="{desc}"' if fixed else "") + ">")
        elif b[0] == "form":
            out.append('<form method="post">')
            for tag, name, label, has_id in b[1]:
                ident = name if (has_id or fixed) else None
                if fixed:
                    out.append(f'<label for="{name}">{label}</label>')
                attrs = f'name="{name}" data-label="{label}"' + (f' id="{ident}"' if ident else "")
                out.append(f"<{tag} {attrs}></{tag}>" if tag != "input" else f"<input {attrs}>")
            out.append('<input type="submit" value="Send"></form>')
        elif b[0] == "button":
            out.append(f'<button class="icon" data-action="{b[1]}"' + (f' aria-label="{b[1]}"' if fixed else "")
                       + '><svg aria-hidden="true"></svg></button>')
        else:
            _, href, vague, title = b
            out.append(f'<p>More: <a href="{href}" title="{title}">{title if fixed else vague}</a></p>')
    out += ["</body>", "</html>"]
    return "\n".join(out) + "\n"


class Dom(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.elements, self.text, self.stack = [], [], []

    def handle_starttag(self, tag, attrs):
        self.elements.append({"tag": tag, "attrs": dict(attrs), "text": ""})
        if tag not in ("img", "input"):
            self.stack.append(self.elements[-1])

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1]["tag"] == tag:
            self.stack.pop()

    def handle_data(self, data):
        if data.strip():
            self.text.append(data.strip())
            if self.stack:
                self.stack[-1]["text"] += data


def parse(html):
    d = Dom()
    d.feed(html)
    return d


def violations(dom, locale):
    v = set()
    html = [e for e in dom.elements if e["tag"] == "html"]
    if not html or html[0]["attrs"].get("lang") != locale:
        v.add("A1")
    for e in dom.elements:
        a = e["attrs"]
        if e["tag"] == "img":
            want = "" if "decorative" in (a.get("class") or "") else a.get("data-description")
            if a.get("alt") != want:
                v.add("A2")
        if e["tag"] in ("input", "select", "textarea") and a.get("type") not in ("hidden", "submit"):
            ident = a.get("id")
            labels = [x for x in dom.elements if x["tag"] == "label" and x["attrs"].get("for") == ident]
            if not ident or ident != a.get("name") or not labels or labels[0]["text"].strip() != a.get("data-label"):
                v.add("A3")
        if e["tag"] == "button" and not e["text"].strip() and a.get("aria-label") != a.get("data-action"):
            v.add("A5")
        if e["tag"] == "a" and (e["text"].strip().lower() in VAGUE or e["text"].strip() != a.get("title")):
            v.add("A6")
    level = 0
    for e in dom.elements:
        if e["tag"] in ("h1", "h2", "h3", "h4", "h5", "h6"):
            n = int(e["tag"][1])
            if n > level + 1:
                v.add("A4")
            level = n
    return v


def generate(seed, out=None):
    rng = rng_for(seed, "plan")
    topics = ["pricing", "security", "about", "careers", "api", "mobile", "enterprise", "startups", "partners",
              "support", "status", "blog", "privacy", "terms", "integrations", "roadmap", "customers", "events"]
    pages = rng.sample([f"{t}-{k}" for t in topics for k in ("overview", "details", "faq")], N_PAGES)
    config = {}
    files = {"docs/A11Y.md": A11Y_MD}
    truth = {"seed": seed, "pages": {}}
    for page in pages:
        prng = rng_for(seed, "page", page)
        locale = prng.choice(LOCALES)
        config[page] = {"locale": locale, "section": page.split("-")[0]}
        blocks = model(prng, page)
        broken = render(page, locale, blocks, fixed=False)
        files[f"site/pages/{page}.html"] = broken
        truth["pages"][page] = {"locale": locale, "fixed": render(page, locale, blocks, fixed=True),
                                "unit_chars": len(broken) + 1500}
    files["site/pages.json"] = json.dumps(config, indent=2, sort_keys=True) + "\n"
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth


A11Y_MD = """# Accessibility rules

Every page under `site/pages/` must pass all six.

- **A1** `<html>` has `lang` set to the page's locale in `site/pages.json`.
- **A2** Every `<img>` has `alt`. Decorative images (class `decorative`) use
  `alt=""`. Every other image uses exactly its `data-description` text.
- **A3** Every form field (`input`, `select`, `textarea`, except submit and
  hidden inputs) has a `<label for="...">` whose text is exactly the field's
  `data-label`. A field without an `id` gets its `name` as its `id`.
- **A4** Headings do not skip levels: a heading is at most one level deeper
  than the heading before it. Fix the level; keep the text.
- **A5** A button with no visible text has `aria-label` equal to its `data-action`.
- **A6** Links do not use vague text ("click here", "read more", "here"). Use
  the link's `title` as its text.

Change nothing else: all other text, elements and attributes stay as they are.
"""


def _signature(dom):
    """What must not change: every element's tag family and its original
    attributes, and all text outside links and headings."""
    sig = []
    for e in dom.elements:
        tag = "h" if e["tag"] in ("h1", "h2", "h3", "h4", "h5", "h6") else e["tag"]
        if tag == "label":
            continue
        attrs = {k: v for k, v in e["attrs"].items() if k not in ("alt", "aria-label", "lang", "id")}
        sig.append((tag, tuple(sorted(attrs.items()))))
    text = [e["text"].strip() for e in dom.elements if e["tag"] in ("p", "title") and e["text"].strip()]
    heads = [e["text"].strip() for e in dom.elements if e["tag"].startswith("h") and e["tag"][1:].isdigit()]
    return sig, text, heads


def grade(seed, workspace):
    """Per page, all or nothing: no rule broken and nothing else changed."""
    truth = generate(seed)
    per = {}
    for page, t in truth["pages"].items():
        path = Path(workspace) / "site" / "pages" / f"{page}.html"
        if not path.exists():
            per[page] = 0.0
            continue
        got = parse(path.read_text())
        want = parse(t["fixed"])
        per[page] = float(not violations(got, t["locale"]) and _signature(got) == _signature(want))
    return {"reward": round(sum(per.values()) / len(per), 4), "pages": per}


def solve(seed, workspace):
    for page, t in generate(seed)["pages"].items():
        write(Path(workspace) / "site" / "pages", f"{page}.html", t["fixed"])


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [p["unit_chars"] for p in t["pages"].values()],
            "judgement_turns": 5, "orchestration_turns": 10, "shared_chars": len(A11Y_MD) + 3000}


ANSWER_PATH = "/workspace"
INSTRUCTION = """\
# Pass the accessibility audit

The pages under `/workspace/site/pages/` failed our accessibility audit. Fix
every page so it meets all the rules in `docs/A11Y.md`, changing nothing else.
Page locales are in `site/pages.json`.
"""

META = {
    "unit": "page", "kind": "markup repair", "domain": "web accessibility", "output_tokens": 1500, "needs_pytest": False,
    "failure_mode": "precise markup fixes whose values come from per-element data, with no collateral change",
    "deliverable": "fixed `site/pages/*.html`",
    "grading": "Per page, all or nothing: an HTML checker finds no rule broken, and every other element, "
               "attribute and text is unchanged. Reward is the mean.",
    "per_unit": "find every failing element on the page, take each fix's value from the right place "
                "(pages.json, data-description, data-label, data-action, title), and fix heading levels in order",
    "traps": [
        "**Locales are per page**, only in pages.json.",
        "**Decorative images need `alt=\"\"`**, not a description.",
        "**Labels need matching ids**, and a field without an id gets its name.",
        "**Heading fixes cascade**: lowering one heading can change what the next may be.",
        "**Collateral edits** (reformatted text, dropped attributes) fail the page.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=False)


if __name__ == "__main__":
    main()
