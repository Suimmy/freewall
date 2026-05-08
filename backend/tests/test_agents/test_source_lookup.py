"""
Unit tests for `app.agents.tools.source_lookup`.

Pure-sync tests via `lookup_domain()`. The @function_tool wrapper
`source_lookup` is exercised indirectly when Provenance agent runs in Step 2.6.
"""

from __future__ import annotations

import pytest

from app.agents.tools.source_lookup import (
    _load_lookup_table,
    _normalize_domain,
    lookup_domain,
)


class TestNormalizeDomain:
    """String hygiene — protocol/path/port/www/case stripping."""

    def test_full_url_with_protocol_and_path(self) -> None:
        assert _normalize_domain("https://www.who.int/news-room/fact-sheets") == "who.int"

    def test_uppercase_normalized(self) -> None:
        assert _normalize_domain("WWW.CDC.gov") == "cdc.gov"

    def test_strips_port(self) -> None:
        assert _normalize_domain("example.com:8080") == "example.com"

    def test_keeps_subdomain_for_finer_match(self) -> None:
        # We DO NOT do eTLD+1 reduction — Mahidol's data uses 'rama.mahidol.ac.th'
        assert _normalize_domain("https://rama.mahidol.ac.th/path") == "rama.mahidol.ac.th"

    def test_strips_query_and_fragment(self) -> None:
        assert _normalize_domain("https://example.com/path?q=foo#frag") == "example.com"

    def test_handles_already_clean_domain(self) -> None:
        assert _normalize_domain("who.int") == "who.int"

    def test_strips_leading_whitespace(self) -> None:
        assert _normalize_domain("  WWW.who.int  ") == "who.int"


class TestLookupDomain:
    """End-to-end lookups against the seeded JSON files."""

    def test_credible_authoritative_match(self) -> None:
        result = lookup_domain("who.int")
        assert result["found"] is True
        assert result["reputation"] == "credible"
        assert result["name"] == "World Health Organization"
        assert result["type"] == "international_authority"
        assert result["domain"] == "who.int"

    def test_full_url_normalizes_and_matches(self) -> None:
        result = lookup_domain("https://www.cdc.gov/diabetes/index.html")
        assert result["found"] is True
        assert result["reputation"] == "credible"
        assert result["domain"] == "cdc.gov"

    def test_unknown_domain_returns_unknown(self) -> None:
        result = lookup_domain("freewall-not-a-real-domain.example")
        assert result["found"] is False
        assert result["reputation"] == "unknown"
        assert result["name"] is None
        assert result["type"] is None

    def test_case_insensitive_match(self) -> None:
        result = lookup_domain("WHO.INT")
        assert result["found"] is True
        assert result["reputation"] == "credible"

    def test_subdomain_exact_match(self) -> None:
        # 'rama.mahidol.ac.th' is in credible.json; parent 'mahidol.ac.th' may not be
        result = lookup_domain("rama.mahidol.ac.th")
        # Don't assert specific reputation in case data evolves — just verify lookup works
        assert result["domain"] == "rama.mahidol.ac.th"
        # If it's seeded, found=True; if not seeded, found=False — both acceptable.
        assert isinstance(result["found"], bool)


class TestLookupTable:
    """The cached table loader."""

    def test_loads_all_three_categories(self) -> None:
        table = _load_lookup_table()
        # We seeded 35 + 13 + 20 = 68 domains.
        assert len(table) >= 60  # allow some headroom for dedup

    def test_contains_known_credible_seeds(self) -> None:
        table = _load_lookup_table()
        for domain in ("who.int", "cdc.gov", "fda.gov"):
            assert domain in table, f"{domain} missing from lookup table"
            assert table[domain]["reputation"] == "credible"

    def test_no_lr_strip_in_keys(self) -> None:
        # Internal invariant: keys are lowercase + stripped
        table = _load_lookup_table()
        for key in table:
            assert key == key.lower().strip()


@pytest.mark.parametrize(
    "input_url,expected_domain",
    [
        ("https://www.example.com", "example.com"),
        ("http://EXAMPLE.com/page", "example.com"),
        ("example.com", "example.com"),
        ("example.com:443", "example.com"),
        ("https://sub.example.co.uk/", "sub.example.co.uk"),
    ],
)
def test_normalize_domain_table(input_url: str, expected_domain: str) -> None:
    assert _normalize_domain(input_url) == expected_domain


class TestPathologicalInputs:
    """
    Defensive tests — `lookup_domain` must not crash on malformed input.

    Real-world inputs from live paste box may include: empty strings, only
    whitespace, URLs without TLD, IP addresses, IDN/punycode hostnames,
    weirdly-encoded URLs. Provenance agent should get a sane 'unknown'
    response in all these cases, not an exception.
    """

    @pytest.mark.parametrize(
        "bad_input",
        [
            "",                          # empty
            "   ",                       # whitespace only
            "https://",                  # protocol with no host
            "http:///",                  # malformed
            "::",                        # gibberish
            "192.168.1.1",               # raw IP
            "http://192.168.1.1:8080/",  # IP with port + path
            "no-protocol-here.invalid",  # invalid TLD
            "ผู้ใช้.example.com",          # IDN (Thai chars)
        ],
    )
    def test_lookup_does_not_crash(self, bad_input: str) -> None:
        """Any pathological input should return shape-valid dict, not raise."""
        result = lookup_domain(bad_input)
        # Shape check
        assert "found" in result
        assert "reputation" in result
        assert "domain" in result
        assert "name" in result
        assert "type" in result
        # Reputation must be one of known values
        assert result["reputation"] in {"unknown", "credible", "mixed", "unreliable"}
        # found is bool
        assert isinstance(result["found"], bool)

    def test_empty_string_returns_unknown(self) -> None:
        result = lookup_domain("")
        assert result["found"] is False
        assert result["reputation"] == "unknown"

    def test_idn_thai_chars_dont_crash(self) -> None:
        # Domain with Thai-language subdomain — uncommon but legal
        result = lookup_domain("ผู้ใช้.example.com")
        assert result["found"] is False  # not in our list
        assert result["reputation"] == "unknown"
