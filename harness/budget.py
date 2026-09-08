"""Token budgeting (DESIGN.md 5.7, 8.1).

Budgets are denominated in tokens, never currency. mini-swe-agent's own
`cost_limit` is in dollars, which would buy a cheap model more work than an
expensive one at nominally equal budget -- mixing model price into a metric
about delegation skill.
"""


class BudgetExceeded(Exception):
    """Raised when a step would take the episode past its token cap."""


class EstimatingCounter:
    """A rough local counter for dry runs. Never valid for reported results.

    Real token counts come from the provider's own counter. An estimate is fine
    for exercising the harness offline, and the exactness flag rides along in the
    artifact so a scorecard can refuse to report an estimated run.
    """

    exact = False

    def __call__(self, text):
        return max(1, len(text) // 4)


class TokenBudget:
    """Tracks token spend against a cap.

    The counter is a required argument on purpose: there is no default that
    silently estimates. A caller that wants an estimate has to say so.
    """

    def __init__(self, max_tokens, counter):
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        self.max_tokens = max_tokens
        self._counter = counter
        self.spent = 0

    @property
    def exact(self):
        return getattr(self._counter, "exact", True)

    @property
    def remaining(self):
        return max(0, self.max_tokens - self.spent)

    @property
    def exhausted(self):
        return self.spent >= self.max_tokens

    def charge(self, text):
        self.spent += self._counter(text)
        return self.spent

    def check(self):
        if self.exhausted:
            raise BudgetExceeded(
                f"spent {self.spent} of {self.max_tokens} tokens"
            )

    def snapshot(self):
        return {
            "max_tokens": self.max_tokens,
            "spent_tokens": self.spent,
            "over_budget": self.spent > self.max_tokens,
            "tokens_exact": self.exact,
        }
