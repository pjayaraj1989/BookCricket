#!/usr/bin/env python3
"""
Fetch player photos for BookCricket from Wikimedia Commons.

Only images under a redistributable licence (CC0, public domain, CC BY,
CC BY-SA, and a few government open-data licences) are downloaded, so they
can legally be bundled with the game and self-hosted. Each photo is saved
under the game's own filename convention

    resources/players/pics/<slug>.<ext>

where <slug> is the player's name lowercased with runs of non-alphanumeric
characters turned into underscores - the exact rule web/app.py uses to serve
them. Attribution for every downloaded image (required by CC BY / CC BY-SA)
is appended to

    resources/players/pics/ATTRIBUTIONS.txt

Non-free images (CC BY-NC, CC BY-ND, "fair use", non-free Wikipedia-only
uploads) are skipped and reported, never downloaded.

Usage:
    python fetch_player_pics.py                 # every player still missing a pic
    python fetch_player_pics.py --limit 25      # only the first 25 missing
    python fetch_player_pics.py --dry-run       # report only, download nothing
    python fetch_player_pics.py --name "Virat Kohli"   # just one player
    python fetch_player_pics.py --overwrite     # re-fetch even if a pic exists

Requires: requests (already in requirements.txt) and an internet connection.
Be nice to Wikimedia: the script rate-limits itself and sends a descriptive
User-Agent, per their API etiquette.
"""
import argparse
import glob
import json
import os
import re
import sys
import time

import requests

ROOT = os.path.dirname(os.path.abspath(__file__))
PICS_DIR = os.path.join(ROOT, "resources", "players", "pics")
ATTRIB_FILE = os.path.join(PICS_DIR, "ATTRIBUTIONS.txt")
PIC_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
MIME_EXT = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}

# Wikimedia asks every client to identify itself; edit the contact if you like.
USER_AGENT = "BookCricket-pic-fetcher/1.0 (https://github.com/; single-project use)"
WIKI_API = "https://en.wikipedia.org/w/api.php"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
REQUEST_PAUSE = 0.5  # seconds between players, to stay polite

# Redistributable licence markers (matched case-insensitively against the
# Commons "LicenseShortName"). Anything with NC (non-commercial) or ND
# (no-derivatives), or not matched here, is treated as non-free and skipped.
FREE_MARKERS = ("cc0", "public domain", "cc by", "pdm", "godl", "ogl", "gfdl")
NONFREE_MARKERS = ("nc", "nd", "non-free", "fair use")


def slug(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def has_pic(s):
    return any(os.path.isfile(os.path.join(PICS_DIR, s + e)) for e in PIC_EXTENSIONS)


def collect_players():
    """Return (unique, collisions): unique is {slug: name} for players to
    fetch (deduped by slug), collisions is {slug: [names]} for slugs that
    come from more than one spelling (skipped, reported for manual fixing)."""
    by_slug = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "data", "teams_*.json"))):
        data = json.load(open(path))
        for team in data.get("Teams", {}).values():
            for p in team.get("players", []):
                name = (p.get("name") or "").strip()
                if name:
                    by_slug.setdefault(slug(name), set()).add(name)
    collisions = {s: sorted(v) for s, v in by_slug.items() if len(v) > 1}
    unique = {s: sorted(v)[0] for s, v in by_slug.items() if len(v) == 1}
    return unique, collisions


def is_free(license_short):
    if not license_short:
        return False
    lic = license_short.lower()
    # match "nc"/"nd" only as whole licence tokens, so a name like
    # "GODL-India" isn't rejected for the "nd" buried inside "India"
    tokens = re.split(r"[^a-z0-9]+", lic)
    if "nc" in tokens or "nd" in tokens or "non-free" in lic or "fair use" in lic:
        return False
    return any(m in lic for m in FREE_MARKERS)


def strip_html(text):
    return re.sub(r"<[^>]+>", "", text or "").strip()


def wiki_lead_image(session, name):
    """Find a Wikipedia page for the player and return its lead image's
    Commons file title, or None. Tries the plain name, then '<name>
    (cricketer)' if the first is a disambiguation page or has no image."""
    for title in (name, "%s (cricketer)" % name):
        r = session.get(
            WIKI_API,
            params={
                "action": "query", "format": "json", "redirects": 1,
                "titles": title, "prop": "pageimages|pageprops",
                "piprop": "name", "ppprop": "disambiguation",
            },
            timeout=15,
        )
        pages = r.json().get("query", {}).get("pages", {})
        for pg in pages.values():
            if "missing" in pg or "disambiguation" in pg.get("pageprops", {}):
                continue
            if pg.get("pageimage"):
                return "File:" + pg["pageimage"]
    return None


def commons_image(session, file_title):
    """Return dict(url, ext, license, artist, credit) for a Commons file if
    it exists there and is freely licensed, else None."""
    r = session.get(
        COMMONS_API,
        params={
            "action": "query", "format": "json", "titles": file_title,
            "prop": "imageinfo", "iiprop": "extmetadata|url|mime",
            "iiextmetadatafilter": "LicenseShortName|Artist|Credit",
        },
        timeout=15,
    )
    pages = r.json().get("query", {}).get("pages", {})
    for pg in pages.values():
        if "missing" in pg:  # only on en.wikipedia (non-free) -> skip
            return None
        ii = (pg.get("imageinfo") or [{}])[0]
        md = ii.get("extmetadata", {})
        lic = (md.get("LicenseShortName") or {}).get("value", "")
        if not is_free(lic):
            return {"nonfree": lic or "unknown"}
        return {
            "url": ii.get("url"),
            "ext": MIME_EXT.get(ii.get("mime"), ".jpg"),
            "license": lic,
            "artist": strip_html((md.get("Artist") or {}).get("value", "")),
            "credit": strip_html((md.get("Credit") or {}).get("value", "")),
        }
    return None


def download(session, url, dest):
    r = session.get(url, timeout=30, stream=True)
    r.raise_for_status()
    if not r.headers.get("Content-Type", "").startswith("image/"):
        raise ValueError("not an image response")
    with open(dest, "wb") as fh:
        for chunk in r.iter_content(8192):
            fh.write(chunk)
    if os.path.getsize(dest) < 1000:  # guard against tiny/placeholder files
        os.remove(dest)
        raise ValueError("suspiciously small image")


def main():
    ap = argparse.ArgumentParser(description="Fetch player pics from Wikimedia Commons.")
    ap.add_argument("--limit", type=int, default=0, help="stop after N players")
    ap.add_argument("--dry-run", action="store_true", help="report only, download nothing")
    ap.add_argument("--overwrite", action="store_true", help="fetch even if a pic already exists")
    ap.add_argument("--name", help="fetch a single named player")
    args = ap.parse_args()

    os.makedirs(PICS_DIR, exist_ok=True)
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    unique, collisions = collect_players()
    if args.name:
        targets = [(slug(args.name), args.name)]
    else:
        targets = sorted(
            (s, n) for s, n in unique.items() if args.overwrite or not has_pic(s)
        )

    got, nonfree, notfound = [], [], []
    for i, (s, name) in enumerate(targets, 1):
        if args.limit and len(got) + len(nonfree) + len(notfound) >= args.limit:
            break
        print("[%d/%d] %s ..." % (i, len(targets), name), end=" ", flush=True)
        try:
            file_title = wiki_lead_image(session, name)
            info = commons_image(session, file_title) if file_title else None
        except Exception as exc:
            print("error (%s)" % exc)
            notfound.append((name, "request error"))
            time.sleep(REQUEST_PAUSE)
            continue

        if info is None:
            print("no free image found")
            notfound.append((name, "no Commons image"))
        elif "nonfree" in info:
            print("SKIP non-free (%s)" % info["nonfree"])
            nonfree.append((name, info["nonfree"]))
        else:
            dest = os.path.join(PICS_DIR, s + info["ext"])
            if args.dry_run:
                print("would download [%s] %s" % (info["license"], info["url"]))
                got.append((name, s + info["ext"], info["license"], info["artist"], info["url"]))
            else:
                try:
                    download(session, info["url"], dest)
                    print("saved %s [%s]" % (os.path.basename(dest), info["license"]))
                    got.append((name, os.path.basename(dest), info["license"], info["artist"], info["url"]))
                except Exception as exc:
                    print("download failed (%s)" % exc)
                    notfound.append((name, "download error"))
        time.sleep(REQUEST_PAUSE)

    # record attribution for everything downloaded (CC BY / BY-SA need it)
    if got and not args.dry_run:
        new = not os.path.exists(ATTRIB_FILE)
        with open(ATTRIB_FILE, "a") as fh:
            if new:
                fh.write("# Player photo attributions (from Wikimedia Commons)\n")
                fh.write("# file | player | licence | author | source\n\n")
            for name, fn, lic, artist, url in got:
                fh.write("%s | %s | %s | %s | %s\n" % (fn, name, lic, artist or "unknown", url))

    print("\n==== summary ====")
    print("downloaded/free : %d" % len(got))
    print("skipped non-free: %d" % len(nonfree))
    print("not found       : %d" % len(notfound))
    if collisions and not args.name:
        print("name collisions : %d (skipped - fix spelling manually)" % len(collisions))
    if nonfree:
        print("\n-- non-free (source your own / find a free image) --")
        for name, lic in nonfree:
            print("   %-28s %s" % (name, lic))
    if notfound:
        print("\n-- no free image found --")
        for name, why in notfound[:40]:
            print("   %-28s %s" % (name, why))
        if len(notfound) > 40:
            print("   ... and %d more" % (len(notfound) - 40))
    if got and not args.dry_run:
        print("\nAttribution written to resources/players/pics/ATTRIBUTIONS.txt")


if __name__ == "__main__":
    sys.exit(main())
