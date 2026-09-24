The directory `tickets/` holds 60 customer support tickets, one per file.

Find every ticket in which the customer was **actually charged more than once for
a single order**: a real duplicate payment that settled. These do not count:

- an extra line that turned out to be an authorization hold and was released,
- two payments for two different orders,
- a question about whether a double charge *could* happen,
- a double charge by some other merchant.

For each ticket that counts, name the order that was double-charged. Tickets list
several orders; name the one that was charged twice.

Write the result to `answer.json` in the working directory:

```json
{"matches": [{"ticket": "T-1234", "order": "ORD-12345"}]}
```

Scoring is precision and recall over (ticket, order) pairs. Leave out anything you
are not sure is a real duplicate charge.
