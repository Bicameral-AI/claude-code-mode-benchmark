# Copyright © 2026 Bicameral, LLC. All rights reserved. See LICENSE.
"""The synthetic support tickets served by records_server.py.

Built from a fixed seed with a small generator of our own, so every machine and every Python
version produces exactly the same tickets. bin/check.py imports this module to work out the
right answers for tasks M1 and M2.
"""

import os

PER_PAGE = 40
PRODUCTS = ["Atlas", "Beacon", "Cobalt", "Delta", "Ember"]
STATUSES = ["open", "pending", "resolved", "closed"]
PRIORITIES = ["low", "normal", "high", "urgent"]
PLANS = ["Starter", "Team", "Business", "Enterprise"]
SENTENCES = [
    "The customer wrote in after the latest update and described the problem in detail.",
    "They reported that the dashboard took more than a minute to load on Monday morning.",
    "A colleague on the same account could not reproduce the issue from another office.",
    "Support asked for a screen recording and the customer sent one the same afternoon.",
    "The export finished, but the totals in the file did not match the totals on screen.",
    "An engineer traced the difference to a time zone setting on the customer's workspace.",
    "The customer asked whether the outage would be covered by the service agreement.",
    "Billing confirmed the invoice date and the plan the account was on at the time.",
    "A workaround was offered, and the customer said it was acceptable for the short term.",
    "The customer followed up twice by email and once through the in-app chat.",
    "Their administrator had changed the single sign-on settings the week before.",
    "The integration with their data warehouse was paused while the team investigated.",
    "Logs for the affected hour were attached to the internal note on this ticket.",
    "The account manager was copied in because the renewal is due next quarter.",
    "A fix was scheduled for the next release and the customer was told the date.",
    "The customer thanked the team and asked to be told when the change went live.",
    "A second, unrelated question about user roles was split into its own ticket.",
    "The mobile app showed the same behaviour once the cache had been cleared.",
    "Nobody else on that plan had reported the problem in the previous thirty days.",
    "The customer asked for a written summary to share with their finance team.",
]

# Task M2 asks for tickets where the customer was really charged more than once for one
# purchase. These sentences say so without the obvious words (twice, double, duplicate, again),
# so finding them takes reading, not a keyword search.
CHARGED_MORE_THAN_ONCE = [
    "Their card statement lists the March subscription fee two times, a minute apart.",
    "One renewal produced two separate debits of the same amount.",
    "The add-on appears on two consecutive receipts though it was bought once.",
    "The bank shows the same order number against two payments taken on the same day.",
    "A single upgrade was taken from the account and then taken a second time the next morning.",
    "The customer paid once at checkout, and the identical sum left the account a second time that evening.",
]
# And these use the obvious words about something else, so a keyword search finds the wrong tickets.
LOOKS_SIMILAR = [
    "The customer asked whether upgrading would mean being charged twice.",
    "A duplicate of this ticket was closed by the support team.",
    "The account is billed twice a year under their contract.",
    "Billing double-checked the invoice and found it correct.",
    "The customer was worried about a double charge, but the statement showed one payment.",
]
# Task M3 uses the same tickets with wording that does not repeat. In the plain data every body
# is built from the same twenty sentences, so a script can list each distinct sentence once and
# spot the unusual ones without reading the tickets. Here each sentence carries details that
# change from ticket to ticket, in the same order as the lists above.
VARIED = [
    "The customer wrote in on {day} after the {month} update and described the problem in detail.",
    "They reported that the {area} took more than {n} minutes to load on {day} morning.",
    "A colleague in the {city} office could not reproduce the issue on the {area}.",
    "Support asked for a screen recording on {day} and the {role} sent one the same afternoon.",
    "The {area} export finished in {month}, but the totals in the file did not match the totals on screen.",
    "An engineer traced the difference on the {area} to a time zone setting on the {city} workspace.",
    "The {role} asked whether the outage in {month} would be covered by the service agreement.",
    "Billing confirmed the {month} invoice date and the plan the {city} account was on at the time.",
    "A workaround was offered on {day}, and the {role} said it was acceptable for the short term.",
    "The {role} followed up twice by email and {n} times through the in-app chat.",
    "Their {role} had changed the single sign-on settings for the {city} team in {month}.",
    "The integration with their data warehouse was paused for {n} days in {month} while the team investigated.",
    "Logs for the affected hour on {day} were attached to the internal note about the {area}.",
    "The account manager in {city} was copied in because the renewal is due in {month}.",
    "A fix was scheduled for the {month} release and the {role} was told the date on {day}.",
    "The {role} thanked the team on {day} and asked to be told when the change went live.",
    "A second, unrelated question about the {area} was split into its own ticket on {day}.",
    "The mobile app showed the same behaviour on the {area} in {city} once the cache had been cleared.",
    "Nobody else in {city} had reported the problem with the {area} in the previous {n} weeks.",
    "The {role} asked for a written summary to share with the {city} finance team by {day}.",
]
CHARGED_VARIED = [
    "Their card statement for {month} lists the subscription fee two times, {n} minutes apart.",
    "One renewal in {month} produced two separate debits of the same amount on the {city} account.",
    "The add-on appears on two consecutive receipts from {month} though the {role} bought it once.",
    "The bank shows the same order number against two payments taken on the same {day}.",
    "A single upgrade was taken from the account on {day} and then taken a second time the next morning.",
    "The {role} paid once at checkout on {day}, and the identical sum left the account a second time that evening.",
]
SIMILAR_VARIED = [
    "The {role} asked whether upgrading in {month} would mean being charged twice.",
    "A duplicate of this ticket was closed by the {city} support team on {day}.",
    "The account is billed twice a year, in {month}, under the {city} contract.",
    "Billing double-checked the {month} invoice on {day} and found it correct.",
    "The {role} was worried about a double charge, but the {month} statement showed one payment.",
]
SLOTS = {
    "day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "month": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October"],
    "n": ["two", "three", "four", "five", "six", "seven", "eight", "nine"],
    "role": ["administrator", "finance lead", "team manager", "account owner", "IT contact", "office manager"],
    "area": ["dashboard", "reports page", "billing page", "export tool", "search page", "settings page"],
    "city": ["Leeds", "Austin", "Lyon", "Osaka", "Porto", "Tallinn", "Denver", "Cork"],
}
CHARGED_COUNT, SIMILAR_COUNT = 9, 15


class Generator:
    """A linear congruential generator: the same numbers everywhere."""

    def __init__(self, seed):
        self.state = seed

    def below(self, n):
        self.state = (self.state * 6364136223846793005 + 1442695040888963407) % 2**64
        return (self.state >> 33) % n

    def pick(self, items):
        return items[self.below(len(items))]


def _build(count=120, seed=20261116, variant=None):
    variant = variant or os.environ.get("RECORDS_VARIANT") or "plain"
    rng = Generator(seed)
    tickets, bodies = [], []
    for i in range(count):
        # Each body is a list of (which list, which sentence), rendered at the end.
        bodies.append([("base", rng.below(len(SENTENCES))) for _ in range(9 + rng.below(4))])
        tickets.append(
            {
                "id": f"TCK-{1001 + i}",
                "customer": f"Customer {1 + rng.below(60):03d}",
                "plan": rng.pick(PLANS),
                "product": rng.pick(PRODUCTS),
                "status": rng.pick(STATUSES),
                "priority": rng.pick(PRIORITIES),
                "opened": f"2026-{1 + rng.below(10):02d}-{1 + rng.below(28):02d}",
                "refund_requested": 5 * rng.below(101),
            }
        )
    # Plant the triage sentences with a second generator, so the fields above (and M1's answer)
    # are exactly what they were before the triage tasks existed.
    plant = Generator(seed + 7)
    order = list(range(count))
    for i in range(count - 1, 0, -1):
        j = plant.below(i + 1)
        order[i], order[j] = order[j], order[i]
    charged = order[:CHARGED_COUNT]
    similar = order[CHARGED_COUNT : CHARGED_COUNT + SIMILAR_COUNT]
    for k, i in enumerate(charged):
        bodies[i].insert(plant.below(len(bodies[i]) + 1), ("charged", k % len(CHARGED_MORE_THAN_ONCE)))
    for k, i in enumerate(similar):
        bodies[i].insert(plant.below(len(bodies[i]) + 1), ("similar", k % len(LOOKS_SIMILAR)))
    plain = {"base": SENTENCES, "charged": CHARGED_MORE_THAN_ONCE, "similar": LOOKS_SIMILAR}
    varied = {"base": VARIED, "charged": CHARGED_VARIED, "similar": SIMILAR_VARIED}
    detail = Generator(seed + 13)  # a third generator, so varied wording changes nothing else
    for ticket, body in zip(tickets, bodies):
        if variant == "varied":
            parts = [
                varied[which][n].format(**{slot: detail.pick(words) for slot, words in SLOTS.items()})
                for which, n in body
            ]
        else:
            parts = [plain[which][n] for which, n in body]
        ticket["body"] = " ".join(parts)
    return tickets, sorted(tickets[i]["id"] for i in charged)


def make_tickets():
    return _build()[0]


def expected_answer():
    """What M1 asks for: Atlas tickets that are open."""
    hits = [
        t for t in make_tickets() if t["product"] == "Atlas" and t["status"] == "open"
    ]
    return {
        "count": len(hits),
        "total_refund_requested": sum(t["refund_requested"] for t in hits),
        "ids": sorted(t["id"] for t in hits),
    }


def expected_triage():
    """What M2 asks for: tickets where the customer was really charged more than once."""
    ids = _build()[1]
    return {"count": len(ids), "ids": ids}
