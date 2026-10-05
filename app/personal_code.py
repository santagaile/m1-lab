"""Personas koda formāta pārbaude (CR-1). Noteikumi vienkāršoti mācību vajadzībām."""

import re

# 11 cipari vai DDMMYY-NNNNN. Dzimšanas datumu un kontrolciparu nepārbauda (CR-1).
PATTERN = re.compile(r"[0-9]{11}|[0-9]{6}-[0-9]{5}")


def normalize(value: str) -> str | None:
    """Atgriež 11 ciparus vai None, ja formāts nav derīgs. Atstarpes malās noņem."""
    code = value.strip()
    if not PATTERN.fullmatch(code):
        return None
    return code.replace("-", "")
