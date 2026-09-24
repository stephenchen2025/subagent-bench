"""W -- wide sweep. Many tickets; every one has to be read.

N support-ticket threads. The task is to find every ticket in which the customer
was really charged twice for a single order, and to name that order.

The family is built so that a keyword search narrows the work but cannot finish
it (ORCHESTRATOR.md 7):

- Decoys share the positives' vocabulary. A customer who says "charged twice"
  can turn out, three messages later, to have seen an authorization hold that
  was released. Two charges can be for two different orders. A customer can ask
  whether a retry *would* charge them twice.
- Some positives use no trigger word at all ("the money for ORD-x left my
  account a second time").
- Every ticket lists several orders on file and mentions others in passing, so
  naming the right order needs the sentence, not the file.

At N=72 the tickets are ~80k tokens, two and a half of the reference harness's
32k windows. Reading them all is the task; fitting them in one context is not
possible.
"""

import json

from orch.task import DELEGATE, OPTIONAL, OrchTask, rng_for, task_id

FAMILY = "W"
SIZES = (6, 24, 72)
TICKETS_PER_WORKER = 9

NAMES = [
    "Avery Lin", "Jordan Okafor", "Priya Raman", "Mateo Silva", "Hana Sato",
    "Noah Fischer", "Leila Haddad", "Samir Patel", "Grace Mwangi", "Oskar Berg",
    "Yuki Tanaka", "Chloe Martin", "Diego Alvarez", "Amara Nwosu", "Felix Wagner",
    "Ines Duarte", "Kofi Mensah", "Maya Cohen", "Liam O'Neill", "Sofia Rossi",
    "Tomas Novak", "Aisha Karim", "Ben Carter", "Elena Petrova", "Ravi Iyer",
]
AGENTS = ["Dana", "Marcus", "Keiko", "Luis", "Fatima", "Pete", "Rosa", "Arjun"]
PRODUCTS = [
    "standing desk", "espresso grinder", "trail running shoes", "noise-cancelling "
    "headphones", "cast iron skillet", "bike light set", "wool blanket",
    "mechanical keyboard", "water filter pitcher", "camping stove", "yoga mat",
    "desk lamp", "rain jacket", "blender", "carry-on suitcase",
]
BANKS = ["my bank", "my credit union", "the card app", "my online banking", "my statement"]

# --- the sentences that decide a ticket ------------------------------------

# Customer statements that read as a duplicate charge on {o}. Used verbatim by
# real positives AND by the resolved-hold decoy, which is what makes the decoy
# hard: the difference is later in the thread, not in this sentence.
CHARGED_TWICE = [
    "My card was charged two times for order {o}.",
    "I was billed twice for {o} -- same amount, same day.",
    "There are two identical debits on {bank} and both reference {o}.",
    "The payment for {o} went through, and then about an hour later it went through again.",
    "{o} shows up once in my order history, but {bank} shows it paid for on two separate lines.",
    "You took the money for {o} a second time after it had already been paid.",
    "I got two receipts for {o}, and both amounts actually left my account.",
    "Duplicate charge on {o}, please refund one of them.",
    "The {amount} for {o} came out of my account, and then the same {amount} came out again the next morning.",
]

# Agent confirmations that make an uncertain report a real positive.
CONFIRM_REAL = [
    "I've checked with our payments team: both captures for {o} settled, so you were "
    "genuinely charged twice. I've issued a refund for the second one; it should show "
    "within 3-5 business days.",
    "Confirmed on our side -- {o} was captured twice by a retry in our checkout. One "
    "refund of {amount} is on its way to you.",
    "You're right, and I'm sorry. Our records show {o} was settled two times. I've "
    "refunded the duplicate.",
]
UNCERTAIN_OPEN = [
    "I think I might have been charged twice for {o}, but one of the lines on {bank} "
    "still says pending, so I'm not sure yet.",
    "There's an extra line for {o} on {bank}. It could just be a hold -- can you check?",
    "Something looks off with {o}: I see what might be a second payment.",
]
CUSTOMER_CONFIRMS_POSTED = [
    "Update: the second line has now posted, it's no longer pending. So both payments "
    "for {o} actually went through.",
    "Just checked again -- both charges for {o} are settled now, not pending.",
]

# Later messages that turn a charged-twice sentence into a non-event.
RESOLVED_AS_HOLD = [
    "I looked into {o}: the second line is a pre-authorization hold from when the first "
    "card attempt was declined. It was never captured and it's already been released, so "
    "you were only charged once.",
    "Our payment logs show a single capture for {o}. The extra line you saw was an "
    "authorization that expired on its own -- no money was taken for it.",
    "Good news: only one payment for {o} ever settled. The other entry was a temporary "
    "hold and your bank has dropped it.",
]
CUSTOMER_ACCEPTS_HOLD = [
    "Oh, you're right -- I checked {bank} this morning and the second line is gone. "
    "Only one charge. Sorry for the false alarm!",
    "Thanks, I see it now: one payment for {o}, the other one disappeared. All good.",
]

TWO_ORDERS = [
    "I see two charges on {bank} this week, one for {o1} and one for {o2}. Both are "
    "correct -- I ordered twice on purpose -- but could you send me the invoices for my "
    "expense report?",
    "Yes, there were two payments, but they're for two different orders ({o1} and {o2}), "
    "so that's fine. I just need a receipt for each.",
]
HYPOTHETICAL = [
    "The checkout page for {o} timed out. If I try to pay again, will I end up being "
    "charged twice?",
    "Before I retry the payment on {o} -- is there any risk of a double charge?",
]
HYPOTHETICAL_REPLY = [
    "No, you won't be charged twice: the first attempt for {o} failed before capture, so "
    "retrying is safe.",
    "Retrying is safe. Our system blocks a second capture on {o}, so a double charge "
    "can't happen.",
]
OTHER_MERCHANT = [
    "Unrelated, but {bank} double-charged me at a coffee shop last week, so I'm "
    "checking every line carefully now. Anyway, my actual question is about delivery "
    "for {o}.",
    "Not your fault, but my gym billed me twice this month, which is why I'm nervous "
    "about {o}. Everything on your side looks like a single charge, I just wanted to "
    "confirm the delivery date.",
]

# --- filler --------------------------------------------------------------------

CUSTOMER_FILLER = [
    "My earlier order {x} arrived fine, no complaints there.",
    "I've been a customer for a few years and usually everything goes smoothly.",
    "The {product} itself is great, for what it's worth.",
    "Could you also tell me whether {x} qualifies for the extended return window?",
    "I changed my shipping address last month, so please double-check you have the new one.",
    "Tracking for {x} hasn't updated since Tuesday.",
    "I tried the chat widget first but it kept disconnecting.",
    "I'm travelling next week, so email is the best way to reach me.",
    "Is there a way to combine loyalty points from {x} with my next purchase?",
    "Your app logged me out twice while I was looking at this, which didn't help.",
    "The confirmation email for {x} went to my spam folder, so I only just saw it.",
    "I'd rather not call; the hold times last time were very long.",
    "My partner placed {x} on our shared account, in case that matters.",
    "The box for {x} was a bit crushed but the contents were fine.",
    "I'm happy to send screenshots if that helps.",
]
AGENT_FILLER = [
    "Thanks for reaching out, and sorry for the trouble.",
    "I can see all the orders on your account, including {x}.",
    "For {x}, the return window is 30 days from delivery.",
    "I've updated your shipping address on file.",
    "Tracking updates can lag by a day or two with this carrier.",
    "I've added a note to your account so the next agent has the context.",
    "Loyalty points post about a week after an order is delivered.",
    "Let me know if anything else looks off.",
    "I've resent the confirmation email for {x} to the address on file.",
    "Screenshots aren't necessary, but thank you for offering.",
    "Our warehouse shows {x} left on schedule.",
    "If you need an invoice for {x}, you can download it from the Orders page.",
]
UNRELATED_TOPICS = [
    "I need to change the delivery address for {o} before it ships.",
    "The {product} from {o} arrived with a scratch on the side. Can I get a replacement?",
    "How do I reset my password? The reset link keeps expiring.",
    "Can I use a gift card on {o}, or is it too late?",
    "I'd like to return the {product} from {o}; it's the wrong size.",
    "Where is my refund for {o}? You said 5 days and it has been 8.",
]


SIGNATURE = (
    "\n\n{agent}\nCustomer Care, Northwind Outfitters\nHours: Mon-Fri 8am-8pm, Sat 9am-5pm. "
    "Replies to this email reach our support queue; please keep the ticket number in the "
    "subject line so your history stays together. Northwind will never ask for your full "
    "card number or password by email. This message and any attachments are intended "
    "only for the named recipient."
)
CUSTOMER_SIGNOFFS = [
    "\n\nThanks,\n{name}\nSent from my phone -- please excuse typos.",
    "\n\nBest regards,\n{name}",
    "\n\n{name}\n(Please reply by email rather than phone if possible.)",
]
LINE_ITEMS = [
    "USB-C charging cable (2m)", "replacement filter cartridge, 3-pack", "merino socks, "
    "size M", "stainless water bottle, 750ml", "gift wrap", "extended warranty, 2 years",
    "carabiner set", "microfiber cloth", "spare battery pack", "travel pouch",
]
STATUSES = ["delivered", "in transit", "delivered", "label created", "delivered", "returned"]


def _order_details(rng, orders):
    """Per-order detail blocks, as a ticketing system attaches them.

    Deliberately silent on payment captures: the order block must not settle
    the question the thread is about.
    """
    blocks = []
    for order in orders:
        items = rng.sample(LINE_ITEMS, rng.randint(2, 4))
        lines = [f"  - {rng.choice(PRODUCTS)} x1"] + [f"  - {item} x{rng.randint(1, 3)}" for item in items]
        blocks.append(
            f"{order}  placed 2026-{rng.randint(1, 8):02d}-{rng.randint(1, 28):02d}  "
            f"status: {rng.choice(STATUSES)}  total: {_amount(rng)}\n"
            f"  payment method: card ending {rng.randint(1000, 9999)}  "
            f"ship to: {rng.randint(10, 999)} {rng.choice(['Elm', 'Harbor', 'Mill', 'Cedar', 'Oak'])} "
            f"{rng.choice(['St', 'Ave', 'Rd', 'Lane'])}\n" + "\n".join(lines)
        )
    return "Order details:\n" + "\n".join(blocks) + "\n\n"


def _amount(rng):
    return f"${rng.randint(19, 480)}.{rng.randint(0, 99):02d}"


def _fmt(template, rng, **kw):
    kw.setdefault("bank", rng.choice(BANKS))
    kw.setdefault("amount", _amount(rng))
    kw.setdefault("product", rng.choice(PRODUCTS))
    return template.format(**kw)


def _filler(pool, rng, others, n):
    out = []
    for template in rng.sample(pool, n):
        out.append(_fmt(template, rng, x=rng.choice(others)))
    return " ".join(out)


def _thread(rng, name, agent, key_messages, others):
    """Interleave the deciding messages with filler, never at the very top.

    `key_messages` is a list of (speaker, text) in order. Filler messages go
    before, between and after them, so the deciding sentence is somewhere in
    the middle of the thread rather than in its first lines.
    """
    messages = []
    opener = _fmt(rng.choice(UNRELATED_TOPICS), rng, o=rng.choice(others))
    messages.append(("customer", opener + " " + _filler(CUSTOMER_FILLER, rng, others, 3)))
    messages.append(("agent", _filler(AGENT_FILLER, rng, others, 4)))
    for speaker, text in key_messages:
        pool = CUSTOMER_FILLER if speaker == "customer" else AGENT_FILLER
        messages.append((speaker, text + " " + _filler(pool, rng, others, 2)))
        if rng.random() < 0.6:
            other = "agent" if speaker == "customer" else "customer"
            opool = AGENT_FILLER if other == "agent" else CUSTOMER_FILLER
            messages.append((other, _filler(opool, rng, others, 3)))
    for _ in range(rng.randint(1, 2)):
        messages.append(("customer", _filler(CUSTOMER_FILLER, rng, others, 4)))
        messages.append(("agent", _filler(AGENT_FILLER, rng, others, 4)))
    lines = []
    for i, (speaker, text) in enumerate(messages, 1):
        who = name if speaker == "customer" else f"{agent} (support)"
        sign = (rng.choice(CUSTOMER_SIGNOFFS).format(name=name) if speaker == "customer"
                else SIGNATURE.format(agent=agent))
        lines.append(f"--- message {i} from {who} ---\n{text}{sign}\n")
    return "\n".join(lines)


def _ticket(rng, tid, kind, orders):
    name = rng.choice(NAMES)
    agent = rng.choice(AGENTS)
    target = orders[0]
    others = orders[1:]
    amount = _amount(rng)
    fmt = lambda t, **kw: _fmt(t, rng, amount=amount, **kw)  # noqa: E731
    if kind == "pos_direct":
        keys = [("customer", fmt(rng.choice(CHARGED_TWICE), o=target))]
        if rng.random() < 0.5:
            keys.append(("agent", fmt(rng.choice(CONFIRM_REAL), o=target)))
    elif kind == "pos_later":
        keys = [
            ("customer", fmt(rng.choice(UNCERTAIN_OPEN), o=target)),
            ("customer", fmt(rng.choice(CUSTOMER_CONFIRMS_POSTED), o=target)),
            ("agent", fmt(rng.choice(CONFIRM_REAL), o=target)),
        ]
    elif kind == "dec_hold":
        keys = [
            ("customer", fmt(rng.choice(CHARGED_TWICE), o=target)),
            ("agent", fmt(rng.choice(RESOLVED_AS_HOLD), o=target)),
            ("customer", fmt(rng.choice(CUSTOMER_ACCEPTS_HOLD), o=target)),
        ]
    elif kind == "dec_two_orders":
        keys = [("customer", fmt(rng.choice(TWO_ORDERS), o1=target, o2=others[0]))]
    elif kind == "dec_hypothetical":
        keys = [
            ("customer", fmt(rng.choice(HYPOTHETICAL), o=target)),
            ("agent", fmt(rng.choice(HYPOTHETICAL_REPLY), o=target)),
        ]
    elif kind == "dec_other_merchant":
        keys = [("customer", fmt(rng.choice(OTHER_MERCHANT), o=target))]
    else:
        keys = []
    shuffled = list(orders)
    rng.shuffle(shuffled)
    header = (
        f"Ticket {tid}\n"
        f"Customer: {name}\n"
        f"Orders on file: {', '.join(shuffled)}\n"
        f"Opened: 2026-{rng.randint(1, 8):02d}-{rng.randint(1, 28):02d} via "
        f"{rng.choice(['email', 'web form', 'chat transcript'])}\n\n"
    )
    return header + _order_details(rng, shuffled) + _thread(rng, name, agent, keys, others)


KINDS_POSITIVE = ("pos_direct", "pos_later")
KINDS_DECOY = ("dec_hold", "dec_two_orders", "dec_hypothetical", "dec_other_merchant")


def _kinds(rng, n):
    """Roughly 25% positive, 35% decoy, 40% unrelated; never zero of either."""
    n_pos = max(1, round(n * 0.25))
    n_dec = max(2, round(n * 0.35))
    kinds = [rng.choice(KINDS_POSITIVE) for _ in range(n_pos)]
    # Cycle through decoy kinds so each appears before any repeats.
    decoys = list(KINDS_DECOY)
    rng.shuffle(decoys)
    kinds += [decoys[i % len(decoys)] for i in range(n_dec)]
    kinds += ["neg"] * (n - len(kinds))
    rng.shuffle(kinds)
    return kinds


INSTRUCTION = """\
The directory `tickets/` holds {n} customer support tickets, one per file.

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
{{"matches": [{{"ticket": "T-1234", "order": "ORD-12345"}}]}}
```

Scoring is precision and recall over (ticket, order) pairs. Leave out anything you
are not sure is a real duplicate charge.
"""

WORKER_BRIEF = """\
Read each of these support tickets in full: {files}

For each, decide whether the customer was actually charged more than once for a
single order (a real duplicate payment that settled). Not a released authorization
hold, not two payments for two different orders, not a hypothetical question, not
another merchant's double charge. Read the whole thread: the deciding message is
often not the first one.

In your report, list only the tickets that count, one JSON object per line:
{{"ticket": "T-1234", "order": "ORD-12345"}}
If none count, say so.
"""


def generate(size, seed):
    rng = rng_for(FAMILY, size, seed)
    ids = rng.sample(range(1000, 9999), size)
    order_pool = rng.sample(range(10000, 99999), size * 4)
    kinds = _kinds(rng, size)
    files, matches, items = {}, [], []
    for i, (num, kind) in enumerate(zip(ids, kinds)):
        tid = f"T-{num}"
        orders = [f"ORD-{order_pool[i * 4 + j]}" for j in range(4)]
        files[f"tickets/{tid}.txt"] = _ticket(rng, tid, kind, orders)
        items.append(tid)
        if kind in KINDS_POSITIVE:
            matches.append({"ticket": tid, "order": orders[0]})
    kinds_by_ticket = dict(zip(items, kinds))
    matches.sort(key=lambda m: m["ticket"])
    answer = json.dumps({"matches": matches}, indent=2)
    return OrchTask(
        id=task_id(FAMILY, size, seed),
        family=FAMILY,
        size=size,
        seed=seed,
        label=OPTIONAL if size <= 6 else DELEGATE,
        instruction=INSTRUCTION.format(n=size),
        files=files,
        truth={"matches": matches, "kinds": kinds_by_ticket},
        solution=f"cat > answer.json <<'EOF'\n{answer}\nEOF\n",
        work_items=sorted(items),
        oracle_plan=_plan(sorted(items)),
    )


def _plan(items):
    groups = [items[i:i + TICKETS_PER_WORKER] for i in range(0, len(items), TICKETS_PER_WORKER)]
    return [
        {
            "items": group,
            "brief": WORKER_BRIEF.format(files=", ".join(f"tickets/{t}.txt" for t in group)),
        }
        for group in groups
    ]


def merge_reports(reports):
    """Scripted synthesis for oracle-split: union of every worker's JSON lines."""
    found = {}
    for report in reports:
        for line in (report or "").splitlines():
            line = line.strip().strip(",")
            if not (line.startswith("{") and line.endswith("}")):
                continue
            try:
                obj = json.loads(line)
            except ValueError:
                continue
            if isinstance(obj, dict) and "ticket" in obj and "order" in obj:
                found[obj["ticket"]] = obj["order"]
    return {"matches": [{"ticket": t, "order": o} for t, o in sorted(found.items())]}
