"""Metadata-only evidence gate. Provenance and relevance require semantic review."""
import re
from datetime import date

IDENTITY = ("document_id", "canonical_url", "publisher_group", "upstream_group", "content_hash")
FIELDS = IDENTITY + ("claim_id", "claim_kind", "stance", "provenance_verified", "published_at", "retrieved_at")
LABELS = {"Confirmed", "Corroborated", "Single-source", "Unverified", "Conflicting"}
PRIMARY = {"T1", "T2", "T3"}


def _known(value):
    return value.strip().casefold() != "unknown"


def independent_count(rows):
    """Count verified connected components, including transitive duplicate links."""
    groups = []
    for row in rows:
        keys = {(key, row[key].strip()) for key in IDENTITY if _known(row[key])}
        eligible = row["provenance_verified"] == "true" and all(_known(row[k]) for k in IDENTITY[:-1])
        matches = [g for g in groups if g[0] & keys]
        for old_keys, old_eligible in matches:
            keys |= old_keys
            eligible |= old_eligible
            groups.remove((old_keys, old_eligible))
        groups.append((keys, eligible))
    return sum(eligible for _, eligible in groups)


def evidence_errors(pool):
    errors = []
    claims = {}
    for index, row in enumerate(pool, 1):
        if any(not isinstance(row.get(k), str) or not row[k].strip() for k in FIELDS):
            errors.append(f"row {index}: missing evidence metadata")
            continue
        if (row["claim_kind"] not in {"normal", "key_parameter"}
                or row["stance"] not in {"support", "refute", "context"}
                or row["provenance_verified"] not in {"true", "false"}
                or row.get("置信") not in LABELS or not _known(row["claim_id"])):
            errors.append(f"row {index}: invalid evidence metadata")
        for key in ("published_at", "retrieved_at"):
            if key == "published_at" and row[key] == "unknown":
                continue
            try:
                if date.fromisoformat(row[key]).isoformat() != row[key]:
                    raise ValueError()
            except ValueError:
                errors.append(f"row {index}: invalid {key}")
        if row["content_hash"] != "unknown" and not re.fullmatch(r"[0-9a-f]{64}", row["content_hash"]):
            errors.append(f"row {index}: invalid content_hash")
        claims.setdefault(row["claim_id"], []).append(row)
    for claim, rows in claims.items():
        labels = {r["置信"] for r in rows}
        kinds = {r["claim_kind"] for r in rows}
        if len(labels) != 1 or len(kinds) != 1:
            errors.append(f"{claim}: inconsistent claim metadata")
            continue
        if labels != {"Confirmed"}:
            continue
        if any(r["stance"] == "refute" and r["层级"] in PRIMARY for r in rows):
            errors.append(f"{claim}: unresolved credible refutation")
        supports = [r for r in rows if r["stance"] == "support" and r["层级"] in PRIMARY]
        count = independent_count(supports)
        required = 3 if kinds == {"key_parameter"} else 2
        if count < required:
            errors.append(f"{claim}: {count} verified independent groups; requires {required}")
    return errors
