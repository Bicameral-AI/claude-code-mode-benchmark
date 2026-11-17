#!/usr/bin/env python3
# Copyright © 2026 Bicameral, LLC. All rights reserved. See LICENSE.
"""Generate the small Python project that task E1 runs on.

  python3 fixtures/invoice_gen.py DIR            the starting files
  python3 fixtures/invoice_gen.py DIR --solved   the same project with the task done correctly

The project has one function, invoice.money.format_amount, called from 36 places in 15 modules
and one script, written in eight different ways. A unit test covers every call site. Everything
is built from fixed lists and a fixed seed, so every machine gets the same files.
"""

import os
import sys

MODULES = [
    "billing", "refunds", "taxes", "discounts", "shipping", "subscriptions", "payroll", "expenses",
    "ledger", "quotes", "statements", "reminders", "credits", "fees", "summaries",
]  # fmt: skip
NOUNS = [
    "total",
    "balance",
    "deposit",
    "refund",
    "credit",
    "surcharge",
    "rebate",
    "subtotal",
]
CURRENCIES = ["EUR", "USD", "GBP", "JPY", "CHF", "SEK", "NOK", "DKK"]
AMOUNTS = [1234.5, 80, 1999.99, 15.25, 250000, 0.5, 42, 9876.543]
# How each of the 36 call sites is written.
FORMS = (
    ["pos2"] * 14 + ["pos3"] * 6 + ["kw_a", "kw_b", "kw_c", "kw_d", "kw_e"]
    + ["multi"] * 4 + ["alias"] * 3 + ["attr"] * 2 + ["partial", "lambda"]
)  # fmt: skip
STEPS = [
    None,
    "amount = round(amount * 1.2, 2)",
    "amount = amount - 5",
    "amount = abs(amount)",
]


class Generator:
    def __init__(self, seed):
        self.state = seed

    def below(self, n):
        self.state = (self.state * 6364136223846793005 + 1442695040888963407) % 2**64
        return (self.state >> 33) % n


def reference(value, currency, places=2):
    return f"{currency} {value:,.{places}f}"


def plan():
    """The 36 call sites: where each lives, how it is written and what it should return."""
    rng = Generator(4242)
    forms = list(FORMS)
    for i in range(len(forms) - 1, 0, -1):  # a fixed shuffle, so each module gets a mix
        j = rng.below(i + 1)
        forms[i], forms[j] = forms[j], forms[i]
    sites, counts = [], {}
    for n, form in enumerate(forms):
        module = "report" if n < 2 else MODULES[(n - 2) % len(MODULES)]
        k = counts.get(module, 0)
        counts[module] = k + 1
        places = 2
        if form in ("pos3", "kw_b", "kw_c", "kw_e", "multi", "lambda"):
            places = [0, 1, 3][rng.below(3)]
        step = STEPS[rng.below(len(STEPS))]
        given = AMOUNTS[rng.below(len(AMOUNTS))]
        amount = given
        if step:
            scope = {"amount": amount}
            exec(step, {}, scope)  # the same arithmetic the generated function does
            amount = scope["amount"]
        currency = CURRENCIES[rng.below(len(CURRENCIES))]
        sites.append(
            {
                "n": n, "module": module, "name": f"{NOUNS[k]}_label", "form": form,
                "currency": currency, "places": places, "step": step, "given": given,
                "expected": reference(amount, currency, places),
            }
        )  # fmt: skip
    return sites


def call(site, solved):
    """The statement that returns the formatted amount, and any module-level line it needs."""
    f, cur, p = site["form"], site["currency"], site["places"]
    fn = "format_money" if solved else "format_amount"
    cur_arg = f'currency="{cur}"' if solved else f'"{cur}"'
    extra = None
    if f == "pos2":
        text = f"return {fn}(amount, {cur_arg})"
    elif f == "pos3":
        text = f"return {fn}(amount, {cur_arg}, {'places=' if solved else ''}{p})"
    elif f == "kw_a":
        text = f'return {fn}(amount, currency="{cur}")'
    elif f == "kw_b":
        text = f'return {fn}(value=amount, currency="{cur}", places={p})'
    elif f == "kw_c":
        text = f"return {fn}(amount, {cur_arg}, places={p})"
    elif f == "kw_d":
        text = f'return {fn}(currency="{cur}", value=amount)'
    elif f == "kw_e":
        text = f'return {fn}(amount, currency="{cur}", places={p})'
    elif f == "multi":
        last = f"places={p}" if solved else str(p)
        text = (
            f"return {fn}(\n        amount,\n        {cur_arg},\n        {last},\n    )"
        )
    elif f == "alias":
        text = f"return fmt(amount, {cur_arg})"
    elif f == "attr":
        text = f"return money.{fn}(amount, {cur_arg})"
    elif f == "partial":
        extra = f'_in_{cur.lower()} = functools.partial({fn}, currency="{cur}")'
        text = f"return _in_{cur.lower()}(amount)"
    else:  # lambda
        last = f"places={p}" if solved else str(p)
        extra = f"_short_{site['n']} = lambda value: {fn}(value, {cur_arg}, {last})  # noqa: E731"
        text = f"return _short_{site['n']}(amount)"
    return text, extra


def module_source(name, sites, solved):
    fn = "format_money" if solved else "format_amount"
    forms = {s["form"] for s in sites}
    dot = "invoice" if name == "report" else ""
    lines = [f'"""{name.capitalize()}: amounts shown to customers."""', ""]
    if "partial" in forms:
        lines += ["import functools", ""]
    if forms - {"alias", "attr"}:
        lines.append(f"from {dot}.money import {fn}")
    if "alias" in forms:
        lines.append(f"from {dot}.money import {fn} as fmt")
    if "attr" in forms:
        lines.append(
            f"from {dot or '.'} import money" if dot else "from . import money"
        )
    lines.append("")
    body = []
    for s in sites:
        text, extra = call(s, solved)
        if extra:
            lines += [extra, ""]
        body += [
            "",
            f"def {s['name']}(amount):",
            f'    """The {s["name"].split("_")[0]} line."""',
        ]
        if s["step"]:
            body.append("    " + s["step"])
        body += ["    " + text, ""]
    return "\n".join(lines + body).rstrip() + "\n"


def test_source(name, sites):
    target = "scripts.report" if name == "report" else f"invoice.{name}"
    lines = [
        "import unittest",
        "",
        f"import {target} as subject",
        "",
        "",
        f"class {name.capitalize()}Test(unittest.TestCase):",
    ]
    for s in sites:
        lines += [
            f"    def test_{s['name']}(self):",
            f"        self.assertEqual(subject.{s['name']}({s['given']!r}), {s['expected']!r})",
            "",
        ]
    return "\n".join(lines) + '\n\nif __name__ == "__main__":\n    unittest.main()\n'


MONEY = '''"""Formatting for amounts of money."""


def {name}({signature}):
    """Format an amount with its currency code, such as "EUR 1,234.50"."""
    return f"{{currency}} {{value:,.{{places}}f}}"
'''

API_TEST = """import unittest

import invoice.money as money


class MoneyApiTest(unittest.TestCase):
    def test_currency_is_keyword_only(self):
        with self.assertRaises(TypeError):
            money.format_money(1, "EUR")

    def test_places_defaults_to_two(self):
        self.assertEqual(money.format_money(1234.5, currency="EUR"), "EUR 1,234.50")

    def test_old_name_is_gone(self):
        self.assertFalse(hasattr(money, "format_amount"))
        with self.assertRaises(ImportError):
            from invoice.money import format_amount  # noqa: F401


if __name__ == "__main__":
    unittest.main()
"""

README = """# invoice

A small library that prepares the amounts shown on invoices, statements and reports.

Run the tests with:

    python3 -m unittest
"""


def build(target, solved=False):
    sites = plan()
    files = {
        "README.md": README,
        "invoice/__init__.py": "",
        "scripts/__init__.py": "",
        "tests/__init__.py": "",
        "tests/test_money_api.py": API_TEST,
        "invoice/money.py": MONEY.format(
            name="format_money" if solved else "format_amount",
            signature="value, *, currency, places=2"
            if solved
            else "value, currency, places=2",
        ),
    }
    for name in MODULES + ["report"]:
        mine = [s for s in sites if s["module"] == name]
        where = "scripts/report.py" if name == "report" else f"invoice/{name}.py"
        files[where] = module_source(name, mine, solved)
        files[f"tests/test_{name}.py"] = test_source(name, mine)
    for rel, text in files.items():
        path = os.path.join(target, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
    return len(sites)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    print(
        f"{build(sys.argv[1], solved='--solved' in sys.argv)} call sites written to {sys.argv[1]}"
    )
