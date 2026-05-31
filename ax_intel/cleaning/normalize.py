from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


TRACKING_PREFIXES = ("utm_",)
TRACKING_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid"}


def canonicalize_url(url: str) -> str:
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    netloc = parts.netloc.lower()
    path = parts.path.rstrip("/") or "/"
    query_pairs = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key not in TRACKING_KEYS and not key.startswith(TRACKING_PREFIXES)
    ]
    query = urlencode(query_pairs, doseq=True)
    return urlunsplit((scheme, netloc, path, query, ""))

