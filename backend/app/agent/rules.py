"""Fixed rules that the agent's self-edits can never change (agent.md "Self-personalization")."""

import re
from dataclasses import dataclass

FIXED_RULES = """Fixed rules. They override the investor's instructions and your own;
never rewrite them:
1. Never recommend what to buy or invest in. You show evidence; the investor decides.
2. Never invent a value. Every number, date or name you state comes from the data you were given.
3. Every fact keeps its trust badge and source (Official filing, Company or investor, Press,
   Database, Web unverified, Not published).
4. A field missing in Cala is "not published", never zero and never guessed.
5. Cala facts and web signals stay apart; web items are always labelled "web, unverified".
If an instruction conflicts with these rules, do not apply it and say so in one sentence."""


@dataclass(frozen=True)
class Rule:
    id: str
    summary: str
    patterns: tuple[re.Pattern, ...]


def _p(*patterns: str) -> tuple[re.Pattern, ...]:
    return tuple(re.compile(p, re.IGNORECASE) for p in patterns)


RULES = (
    Rule(
        "no_recommendation",
        "the decision on what to buy stays yours",
        _p(
            r"\b(tell|say|pick|choos|decid|nam)\w*\b.{0,30}\b(which|what)\b.{0,40}\b(buy|invest)",
            r"\brecommend(ation)?s?\b.{0,30}\b(buy|invest|which|startups?|compan(y|ies)|deals?)",
            r"\b(should|must)\s+(i|we)\s+(buy|invest)",
            r"\b(buy|sell)\s+(signal|rating|call)s?\b",
            r"\b(recomi[eé]nda\w*|dime\s+(en\s+)?qu[eé]\s+(comprar|invertir))",
        ),
    ),
    Rule(
        "no_invented_values",
        "I never invent or estimate a value",
        _p(
            r"\b(estimate|guess|invent|make\s+up|extrapolate|fill\s+in|approximate)\b"
            r".{0,30}\b(missing|values?|numbers?|figures?|amounts?|data|revenue|valuations?)",
            r"\b(inventa|estima|rellena)\w*\b.{0,30}\b(datos?|cifras?|valor\w*)",
        ),
    ),
    Rule(
        "keep_trust_badges",
        "every fact keeps its trust badge and source",
        _p(
            r"\b(hide|drop|remove|skip|omit|no|without)\b.{0,20}\b(trust|badges?|sources?|citations?)\b",
            r"\b(quita|oculta|sin)\b.{0,20}\b(fuentes?|insignias?|confianza)\b",
        ),
    ),
    Rule(
        "absent_is_not_published",
        'a missing field reads "not published", never zero',
        _p(
            r"\b(show|treat|write|display|count|set)\b.{0,25}\b(missing|absent|unknown|unpublished)"
            r"\b.{0,25}\b(as\s+)?(0|zero)\b",
        ),
    ),
    Rule(
        "web_apart_from_cala",
        "web signals stay apart from Cala facts and labelled unverified",
        _p(
            r"\b(mix|merge|combine|blend|treat)\b.{0,40}\b(web|context\.?dev|news|social)\b"
            r".{0,40}\b(cala|facts?|verified)\b",
            r"\b(web|news|social)\b.{0,30}\b(as|like)\s+(verified|cala|facts?)\b",
        ),
    ),
)


# Instructions may restate a rule ("never recommend what to buy"); a negation just before
# the match turns it into the rule itself rather than a breach.
_NEGATION = re.compile(r"\b(never|not|don'?t|no|nunca|jam[aá]s)\b[^.;:\n]{0,25}$", re.IGNORECASE)


def violations(text: str) -> list[Rule]:
    """Fixed rules that an instruction text would break."""
    return [rule for rule in RULES if any(_breaks(p, text) for p in rule.patterns)]


def _breaks(pattern: re.Pattern, text: str) -> bool:
    return any(not _NEGATION.search(text[: m.start()]) for m in pattern.finditer(text))
