"""Minimal, idempotent portal edits. Read live files before using these functions."""

import re

MARKER = "live-explain-recruitment"


def caddy_patch(source):
    begin, end = "# BEGIN " + MARKER, "# END " + MARKER
    block = """# BEGIN live-explain-recruitment
    redir /live-explain /live-explain/ 308
    handle_path /live-explain/* {
        import media_auth
        reverse_proxy 127.0.0.1:18766
    }
    # END live-explain-recruitment"""
    if not re.search(r"\(media_auth\)\s*\{", source):
        raise ValueError("Existing portal auth snippet media_auth was not found; do not expose this route")
    if begin in source:
        if source.count(begin) != 1 or source.count(end) != 1:
            raise ValueError("Ambiguous Live Explain markers")
        start, stop = source.index(begin), source.index(end) + len(end)
        return source[:start] + block + source[stop:]
    if "/live-explain" in source:
        raise ValueError("Unmarked existing Live Explain route; inspect it before editing")
    site = re.search(r"(?m)^\s*(?:https://)?prol\.aridlin\.pl\s*\{", source)
    if not site:
        raise ValueError("Expected portal site block not found")
    return source[: site.end()] + "\n    " + block + "\n" + source[site.end() :]


def index_patch(source):
    """Match a live simple app link; complex portal cards require human/agent inspection."""
    if 'href="/live-explain/' in source or "href='/live-explain/" in source:
        return source
    # Keep the current portal's navigation style. Only duplicate a simple anchor;
    # never inject into an unknown JS workspace or replace the whole index.
    matches = list(
        re.finditer(
            r'<a\b[^>]*\bhref=["\']/(?:phonomenal|plan|kartkowki)/?["\'][^>]*>[^<]+</a>', source, re.I
        )
    )
    if not matches:
        raise ValueError(
            "Portal uses nontrivial navigation. Inspect the live index and add a matching entry before deployment can finish."
        )
    anchor = matches[0]
    if re.search(r"\s(?:on\w+|data-[\w-]+)\s*=", anchor.group(), re.I):
        raise ValueError("Navigation anchor has custom behavior; inspect the live index before editing")
    clone = re.sub(r'href=(["\'])[^"\']+\1', 'href="/live-explain/"', anchor.group(), count=1)
    clone = re.sub(r'\s+id=(["\'])[^"\']+\1', "", clone)
    clone = re.sub(r">[^<]+</a>$", ">Live Explain</a>", clone)
    presenter = clone.replace('href="/live-explain/"', 'href="/live-explain/presenter/"').replace(
        ">Live Explain</a>", ">Live Explain — prezenter</a>"
    )
    return (
        source[: anchor.end()]
        + "\n<!-- BEGIN "
        + MARKER
        + " -->\n"
        + clone
        + "\n"
        + presenter
        + "\n<!-- END "
        + MARKER
        + " -->"
        + source[anchor.end() :]
    )
