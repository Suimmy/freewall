"""Ingest fact sheets from data/corpus/ into Chroma for RAG retrieval.

Run once after seeding/editing data/corpus/*.md. Embeds each chunk via OpenAI
text-embedding-3-small and upserts into the persistent Chroma DB at
`<repo>/data/corpus/chroma_db/`.

Usage (from repo root):
    uv run --project backend python data/corpus/ingest.py

Or with explicit args:
    cd backend && uv run python ../data/corpus/ingest.py \\
        --corpus-dir ../data/corpus \\
        --chroma-path ../data/corpus/chroma_db

API key is read from backend/.env via pydantic-settings (no shell env pollution).
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Add backend/ to sys.path so we can use app.config (pydantic-settings) +
# app.core.llm (cached OpenAI client). Same pattern as scripts/test_*.py.
_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "backend"))

import chromadb  # noqa: E402

from app.config import settings  # noqa: E402
from openai import OpenAI  # noqa: E402


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)

# Header-based chunking config:
# - Each H2 section becomes one chunk (section_title prepended for embedding context).
# - Sections > MAX_CHUNK_CHARS fall back to char-window split (preserving header per chunk).
# - Sections < MIN_CHUNK_CHARS are kept as-is (small but coherent like "## Overview" stub).
MAX_CHUNK_CHARS = 1000
MIN_CHUNK_CHARS = 80
FALLBACK_OVERLAP = 50


@dataclass
class CorpusChunk:
    """One retrievable chunk + its provenance metadata."""

    text: str
    source_url: str
    source_org: str  # WHO, CDC, Mayo, DDC, MOPH, Mahidol
    lang: str  # "en" | "th"
    topic: str
    section: str  # H2 header from .md (e.g., "Treatment", "การป้องกัน"). "" for pre-first-header.
    file_path: str  # relative to data/corpus/
    chunk_idx: int


def parse_frontmatter(md_text: str) -> tuple[dict[str, str], str]:
    """Split YAML-like frontmatter from body. Returns ({}, full_text) if no frontmatter."""
    match = FRONTMATTER_RE.match(md_text)
    if not match:
        return {}, md_text
    fm_block, body = match.group(1), match.group(2)
    fm: dict[str, str] = {}
    for line in fm_block.strip().splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm, body


def _char_split(text: str, size: int, overlap: int) -> list[str]:
    """Char-window fallback used only when an H2 section exceeds MAX_CHUNK_CHARS."""
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks


def chunk_by_headers(
    body: str,
    max_size: int = MAX_CHUNK_CHARS,
) -> list[tuple[str, str]]:
    """
    Split markdown body into chunks at H2 (`## `) boundaries.

    Returns list of (section_title, chunk_text) pairs. The chunk_text includes
    the `## title` prefix so the embedding model sees topical context.

    For sections larger than `max_size`, fall back to char-window splitting —
    each sub-chunk re-prepends the H2 header to keep the section context.

    Skips H1 (`# Title`) and content before the first H2.
    """
    sections: list[tuple[str, list[str]]] = []  # [(title, body_lines), ...]
    current_title: str | None = None
    current_lines: list[str] = []

    for line in body.splitlines():
        # Treat H2 as section boundary; ignore H1 (file title) and H3+ (subsection within).
        if line.startswith("## ") and not line.startswith("### "):
            if current_title is not None:
                sections.append((current_title, current_lines))
            current_title = line[3:].strip()
            current_lines = []
        elif current_title is not None:
            current_lines.append(line)
    if current_title is not None:
        sections.append((current_title, current_lines))

    chunks: list[tuple[str, str]] = []
    for title, lines in sections:
        section_body = "\n".join(lines).strip()
        if not section_body or len(section_body) < MIN_CHUNK_CHARS - len(title) - 4:
            # Too small to be useful even with header — skip.
            continue
        full = f"## {title}\n\n{section_body}"
        if len(full) <= max_size:
            chunks.append((title, full))
        else:
            # Big section — char-split the body, re-prepend header to each sub-chunk.
            for sub in _char_split(section_body, size=max_size - len(title) - 8,
                                   overlap=FALLBACK_OVERLAP):
                chunks.append((title, f"## {title}\n\n{sub}"))
    return chunks


def load_corpus(corpus_dir: Path) -> list[CorpusChunk]:
    """Walk corpus_dir, parse all .md files, yield H2-section-based chunks."""
    out: list[CorpusChunk] = []
    for md_path in corpus_dir.rglob("*.md"):
        if md_path.name == "README.md":
            continue
        text = md_path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        rel = md_path.relative_to(corpus_dir).as_posix()
        for idx, (section, chunk) in enumerate(chunk_by_headers(body)):
            out.append(
                CorpusChunk(
                    text=chunk,
                    source_url=fm.get("source_url", ""),
                    source_org=fm.get("source_org", ""),
                    lang=fm.get("lang", "en"),
                    topic=fm.get("topic", ""),
                    section=section,
                    file_path=rel,
                    chunk_idx=idx,
                )
            )
    return out


_DEFAULT_CORPUS_DIR = _REPO_ROOT / "data" / "corpus"
_DEFAULT_CHROMA_PATH = _REPO_ROOT / "data" / "corpus" / "chroma_db"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus-dir", type=Path, default=_DEFAULT_CORPUS_DIR)
    parser.add_argument("--chroma-path", type=Path, default=_DEFAULT_CHROMA_PATH)
    parser.add_argument("--collection", default="freewall_corpus")
    parser.add_argument("--embed-model", default="text-embedding-3-small")
    parser.add_argument("--reset", action="store_true",
                        help="Delete existing collection before ingesting (clean rebuild)")
    args = parser.parse_args()

    chunks = load_corpus(args.corpus_dir)
    print(f"Loaded {len(chunks)} chunks from {args.corpus_dir}")
    if not chunks:
        print("No .md files found — exiting.")
        return

    args.chroma_path.mkdir(parents=True, exist_ok=True)
    chroma = chromadb.PersistentClient(path=str(args.chroma_path))

    if args.reset:
        try:
            chroma.delete_collection(args.collection)
            print(f"Deleted existing collection '{args.collection}'")
        except Exception:
            pass  # didn't exist
    collection = chroma.get_or_create_collection(args.collection)

    print(f"Embedding {len(chunks)} chunks via {args.embed_model}...")
    openai_client = OpenAI(api_key=settings.openai_api_key)
    # Single batched call — OpenAI embeddings endpoint accepts a list and is much
    # faster + cheaper than per-chunk calls (one round-trip vs N).
    response = openai_client.embeddings.create(
        model=args.embed_model,
        input=[c.text for c in chunks],
    )
    embeddings = [item.embedding for item in response.data]
    usage_total = getattr(response, "usage", None)
    if usage_total is not None:
        # text-embedding-3-small: $0.02 / 1M tokens
        cost = usage_total.total_tokens * 0.02 / 1_000_000
        print(f"  embedded {usage_total.total_tokens:,} tokens (~${cost:.4f})")

    print(f"Upserting {len(chunks)} chunks into '{args.collection}'...")
    collection.upsert(
        ids=[f"{c.file_path}::{c.chunk_idx}" for c in chunks],
        embeddings=embeddings,
        documents=[c.text for c in chunks],
        metadatas=[
            {
                "source_url": c.source_url,
                "source_org": c.source_org,
                "lang": c.lang,
                "topic": c.topic,
                "section": c.section,
                "file_path": c.file_path,
                "chunk_idx": c.chunk_idx,
            }
            for c in chunks
        ],
    )
    print(f"Done. Collection now has {collection.count()} chunks.")
    by_org: dict[str, int] = {}
    by_lang: dict[str, int] = {}
    for c in chunks:
        by_org[c.source_org] = by_org.get(c.source_org, 0) + 1
        by_lang[c.lang] = by_lang.get(c.lang, 0) + 1
    print(f"  by org:  {by_org}")
    print(f"  by lang: {by_lang}")


if __name__ == "__main__":
    main()
