"""DEPRECATED 2026-05-07 (CLAUDE.md decision #20): no longer used.

Sheets curation workflow was dropped after team meeting voted no on 200-post effort.
Active curation = 20 prefilled posts in demo/site/examples.json (Suim curates directly).
File retained for traceability — do not run.

---

Original purpose:
Convert Google Sheets CSV export → posts_raw.jsonl.

Usage (from repo root):
    cd data/tools
    python sheets_to_jsonl.py

Default paths:
    input:  ../source_posts/posts_raw.csv  (Sheets export, gitignored)
    output: ../source_posts/posts_raw.jsonl (gitignored)

The script:
    1. Reads CSV (utf-8-sig to handle Excel BOM)
    2. Drops the `author_real` column (stays in Sheets only — never enters JSONL)
    3. Splits `image_urls` on commas → list
    4. Validates: required fields, language, category_hint, length sanity
    5. Writes JSONL (one object per line)
    6. Prints distribution summary (count by language + category)

Standalone — no third-party deps. Run with system python or any uv venv.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

# Fail loud if anyone accidentally runs this — see header.
if __name__ == "__main__":
    print("ERROR: sheets_to_jsonl.py is deprecated (CLAUDE.md decision #20).", file=sys.stderr)
    print("       Sheets curation workflow no longer in scope.", file=sys.stderr)
    print("       See docstring for context.", file=sys.stderr)
    sys.exit(1)

# These mirror the SPEC + Sheets dropdowns. Keep in sync.
ALLOWED_LANGUAGE = {"th", "en"}
ALLOWED_PLATFORM = {
    "facebook.com",
    "x.com",
    "reddit.com",
    "tiktok.com",
    "instagram.com",
    "line",
    "web",
}
ALLOWED_CATEGORY = {
    "anti_vaccine",
    "supplement",
    "cancer_myth",
    "diet_fad",
    "covid_misinfo",
    "mental_health_misinfo",
    "legit_health",
}
ALLOWED_COLLECTOR = {"B", "C", "D", "E", "Suim"}

REQUIRED_FIELDS = (
    "id",
    "url",
    "platform",
    "author_anon",
    "captured_at",
    "language",
    "text",
    "category_hint",
    "collector",
)


def parse_image_urls(raw: str) -> list[str]:
    if not raw or not raw.strip():
        return []
    return [u.strip() for u in raw.split(",") if u.strip()]


def validate_row(row: dict[str, str], lineno: int) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if not row.get(field, "").strip():
            errors.append(f"line {lineno}: missing required field '{field}'")

    language = row.get("language", "").strip()
    if language and language not in ALLOWED_LANGUAGE:
        errors.append(f"line {lineno}: invalid language '{language}' (allowed: {ALLOWED_LANGUAGE})")

    platform = row.get("platform", "").strip()
    if platform and platform not in ALLOWED_PLATFORM:
        errors.append(f"line {lineno}: invalid platform '{platform}' (allowed: {ALLOWED_PLATFORM})")

    category = row.get("category_hint", "").strip()
    if category and category not in ALLOWED_CATEGORY:
        errors.append(f"line {lineno}: invalid category_hint '{category}' (allowed: {ALLOWED_CATEGORY})")

    collector = row.get("collector", "").strip()
    if collector and collector not in ALLOWED_COLLECTOR:
        errors.append(f"line {lineno}: invalid collector '{collector}' (allowed: {ALLOWED_COLLECTOR})")

    text = row.get("text", "").strip()
    if text and len(text) < 50:
        errors.append(f"line {lineno}: text very short ({len(text)} chars) — likely incomplete")
    if text and len(text) > 5000:
        errors.append(f"line {lineno}: text very long ({len(text)} chars) — please trim or split")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).parent / ".." / "source_posts" / "posts_raw.csv",
        help="CSV export from Google Sheets",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent / ".." / "source_posts" / "posts_raw.jsonl",
        help="Output JSONL path",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on any validation error (default: warn but continue)",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"❌ Input not found: {args.input}", file=sys.stderr)
        print("   Did you File → Download → Comma-separated values from Sheets first?", file=sys.stderr)
        return 1

    rows_kept: list[dict] = []
    all_errors: list[str] = []
    by_language: Counter = Counter()
    by_category: Counter = Counter()
    by_collector: Counter = Counter()

    with args.input.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for lineno, raw_row in enumerate(reader, start=2):  # row 1 is header
            row = {k: (v or "").strip() for k, v in raw_row.items()}
            if not row.get("url"):
                continue  # skip empty rows (Sheets often has blanks down to row 501)

            errors = validate_row(row, lineno)
            if errors:
                all_errors.extend(errors)
                if args.strict:
                    continue

            obj = {
                "id": row["id"],
                "url": row["url"],
                "platform": row["platform"],
                "author": row["author_anon"],  # rename column for downstream consumers
                "captured_at": row["captured_at"],
                "language": row["language"],
                "text": row["text"],
                "image_urls": parse_image_urls(row.get("image_urls", "")),
                "category_hint": row["category_hint"],
                "collector": row["collector"],
                "notes": row.get("notes", ""),
            }
            rows_kept.append(obj)
            by_language[row["language"]] += 1
            by_category[row["category_hint"]] += 1
            by_collector[row["collector"]] += 1

    if all_errors:
        print(f"⚠️  {len(all_errors)} validation issue(s):", file=sys.stderr)
        for err in all_errors[:30]:
            print(f"   {err}", file=sys.stderr)
        if len(all_errors) > 30:
            print(f"   ...and {len(all_errors) - 30} more", file=sys.stderr)
        if args.strict:
            print("❌ Strict mode — exiting without writing output.", file=sys.stderr)
            return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        for obj in rows_kept:
            f.write(json.dumps(obj, ensure_ascii=False))
            f.write("\n")

    print(f"✅ Wrote {len(rows_kept)} posts → {args.output}")
    print()
    print(f"By language:  {dict(by_language)}")
    print(f"By collector: {dict(by_collector)}")
    print("By category:")
    for cat in sorted(by_category):
        print(f"   {cat:30s} {by_category[cat]:>4}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
