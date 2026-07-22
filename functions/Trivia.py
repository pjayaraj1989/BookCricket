"""
Best-effort cricket trivia for the web UI's corner panel while a match is
live: a short Wikipedia snippet about either team, one of the players
currently out in the middle, the venue, one of the umpires, or (as a
fallback, or just for variety) a general cricket topic.

This is pure flavor and never allowed to affect gameplay: every lookup is
short-timeout and fails silently (offline, Wikipedia unreachable, rate
limited, no page found, a disambiguation page, ...) - "if there is internet
connection" is satisfied simply by every fetch attempt quietly returning
None when there isn't one, rather than by any explicit connectivity check.
"""
import random

import requests

_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/%s"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
_TIMEOUT = 4  # seconds - trivia is flavor, never worth a long stall

# evergreen general-cricket topics: used to round out the candidate pool
# every round (variety, even when specific subjects also have pages), and as
# a fallback source of trivia when every specific subject's lookup fails
_GENERAL_TOPICS = [
    "Cricket",
    "Test cricket",
    "One Day International",
    "Twenty20",
    "Duckworth–Lewis–Stern method",
    "Cricket World Cup",
    "The Ashes",
    "Yorker",
    "Googly",
    "Cricket bat",
    "Silly point",
    "Hat-trick",
    "Maiden over",
    "Reverse swing",
    "Doosra",
    "Powerplay (cricket)",
    "Duck (cricket)",
    "Declaration and forfeiture",
    "Follow-on",
    "Century (cricket)",
]


def _fetch_summary(title):
    """
    One Wikipedia page-summary lookup.

    Returns:
        str: a plain-text extract, or None on any failure (offline, 404,
        timeout, rate-limited, a disambiguation page, ...).
    """
    try:
        resp = requests.get(
            _SUMMARY_URL % requests.utils.quote(title),
            headers=_HEADERS,
            timeout=_TIMEOUT,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
    except (requests.RequestException, ValueError):
        return None

    if data.get("type") == "disambiguation":
        return None
    extract = (data.get("extract") or "").strip()
    return extract or None


_MAX_SNIPPET_CHARS = 130


def _first_sentences(text, n=1):
    """A short, panel-sized snippet: the first n sentences of a longer
    extract, hard-capped in length too (a single "sentence" can still run
    long, e.g. one packed with a title/nationality/team clause)."""
    parts = text.replace("\n", " ").split(". ")
    snippet = ". ".join(parts[:n]).strip()
    if snippet and not snippet.endswith("."):
        snippet += "."
    if len(snippet) > _MAX_SNIPPET_CHARS:
        snippet = snippet[:_MAX_SNIPPET_CHARS].rsplit(" ", 1)[0].rstrip(".,;: ") + "…"
    return snippet


def _CandidateSubjects(match):
    """(category, subject) pairs worth trying this round, built from the
    live match state - whichever of team1/team2/current batters/current
    bowler/venue/umpires happen to be set."""
    candidates = []

    def add(category, subject):
        if subject:
            candidates.append((category, subject))

    add("team", getattr(match.team1, "name", None))
    add("team", getattr(match.team2, "name", None))

    bt = getattr(match, "batting_team", None)
    for p in (getattr(bt, "current_pair", None) or []) if bt is not None else []:
        if p is not None:
            add("player", p.name)

    bowl_team = getattr(match, "bowling_team", None)
    bowler = getattr(bowl_team, "current_bowler", None) if bowl_team is not None else None
    if bowler is not None:
        add("player", bowler.name)

    venue = getattr(match, "venue", None)
    add("venue", getattr(venue, "name", None))

    for name in getattr(match, "umpires", None) or []:
        add("umpire", name)

    random.shuffle(candidates)
    # a general topic is always in the running too, alongside the specific
    # subjects above - not just a last-resort fallback
    candidates.append(("general", random.choice(_GENERAL_TOPICS)))
    return candidates


def _titles_to_try(category, subject):
    """
    Wikipedia page title(s) to try for one candidate, in order. A team name
    that matches a country ("Australia", "India", ...) would otherwise
    resolve to the country's own article rather than the cricket team's, so
    team lookups try the cricket-specific title first and fall back to the
    plain name (which is exactly right for a franchise/all-time-XI name
    like "MumbaiIndians" that has no "national cricket team" article).
    """
    if category == "team":
        return [subject + " national cricket team", subject]
    return [subject]


def GetTrivia(match):
    """
    Pick a random subject from the live match (either team, a player
    currently out in the middle, the venue, an umpire, or a general cricket
    topic) and fetch a short Wikipedia snippet about it. Tries a few
    candidates in case one comes up empty (an obscure venue with no page,
    a disambiguation page, ...) before giving up for this round.

    Args:
        match: the live Match.

    Returns:
        dict: {"category", "subject", "text"}, or None if nothing could be
        fetched this round.
    """
    for category, subject in _CandidateSubjects(match)[:4]:
        for title in _titles_to_try(category, subject):
            text = _fetch_summary(title)
            if text:
                return {
                    "category": category,
                    "subject": subject,
                    "text": _first_sentences(text),
                }
    return None
