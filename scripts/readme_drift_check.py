#!/usr/bin/env python3
"""README drift guard — keeps README.md / README_EN.md honest vs the actual repo.

Zero-dependency (stdlib only), offline-safe. CI gate for the Tests workflow.

Checks (exit 1 on any failure):
  R1  both READMEs exist and stay within the 200-line budget
  R2  template-count claim matches reality: five templates (A-E) — the actual
      set in references/templates.md; stale "three templates" claims fail
  R3  FAQ / example pointers target references/ files; dead SKILL.md section
      anchors (extracted to references/ since v2.3.2) fail
  R4  update-history line in each README matches the top CHANGELOG version
  R5  banned stale tokens: files deleted from the repo must not be listed
      in the directory tree
  R6  feature headings carry no version tags — versioned headings rot into
      stale claims (the exact drift this script was created to prevent)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []

readme_cn = (ROOT / "README.md").read_text(encoding="utf-8")
readme_en = (ROOT / "README_EN.md").read_text(encoding="utf-8")
changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

m = re.search(r"^## \[(\d+\.\d+\.\d+)\]", changelog, re.MULTILINE)
top_version = m.group(1) if m else None
if not top_version:
    errors.append("R4: cannot parse top version from CHANGELOG.md")

for name, text in (("README.md", readme_cn), ("README_EN.md", readme_en)):
    lines = text.count("\n") + 1
    if lines > 200:
        errors.append(f"R1: {name} exceeds the 200-line budget ({lines} lines)")

    # R2 — template claim matches the actual A-E set
    if name == "README.md":
        if "五套模板" not in text:
            errors.append(f"R2: {name} lost the five-template claim (templates A-E)")
    else:
        if "Five templates" not in text:
            errors.append(f"R2: {name} lost the five-template claim (templates A-E)")
    if "三套模板" in text or "Three templates" in text:
        errors.append(f"R2: {name} still claims three templates (stale)")

    # R3 — FAQ/example pointers must target references/, not dead SKILL.md anchors
    if "references/faq.md" not in text:
        errors.append(f"R3: {name} must point the FAQ at references/faq.md")
    if "references/example.md" not in text:
        errors.append(f"R3: {name} must point the example at references/example.md")
    for dead in ("第八节", "第九节", "Section 8 · FAQ", "Section 9 · Full Example"):
        if dead in text:
            errors.append(f"R3: {name} references dead SKILL.md anchor {dead!r} (content lives in references/)")

    # R4 — update-history line tracks the CHANGELOG top version
    if top_version:
        hm = re.search(r"完整更新史.*?(v[\d.]+ → v[\d.]+)|Full changelog.*?(v[\d.]+ → v[\d.]+)", text)
        if not hm or top_version not in hm.group(0):
            errors.append(f"R4: {name} update-history line does not reach CHANGELOG top version v{top_version}")

    # R5 — banned stale tokens
    if "release_body.md" in text:
        errors.append(f"R5: {name} still lists release_body.md (deleted, gitignored scratch)")

    # R6 — version-tagged headings rot into stale claims
    for pat in ("特性（v", "Features (v"):
        if pat in text:
            errors.append(f"R6: {name} carries a version-tagged features heading {pat!r} — describe capabilities, not versions")

if errors:
    print("README DRIFT GATE FAILED:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(f"README DRIFT GATE PASSED (CHANGELOG top v{top_version})")
