import re

COMMON_FIXES = {
    r"\bintenship\b": "internship",
    r"\bintership\b": "internship",
    r"\bproj(?:ect)?s?\b": "project",
}

def normalize_query(q: str) -> str:
    q = (q or "").strip()
    for pat, repl in COMMON_FIXES.items():
        q = re.sub(pat, repl, q, flags=re.IGNORECASE)
    return q


