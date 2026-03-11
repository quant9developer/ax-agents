from enterprise_ai_platform.mcp.browser_bridge import parse_duckduckgo_results


def test_parse_duckduckgo_results_extracts_items() -> None:
    html = """
    <html>
      <body>
        <a class="result__a" href="https://example.com/article-1">AI Agents In Retail</a>
        <div class="result__snippet">Retailers are adopting AI agents for support and automation.</div>
        <a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Farticle-2">Second Result</a>
        <div class="result__snippet">Another snippet for the second result.</div>
      </body>
    </html>
    """

    items = parse_duckduckgo_results(html, limit=2)

    assert len(items) == 2
    assert items[0]["title"] == "AI Agents In Retail"
    assert items[0]["url"] == "https://example.com/article-1"
    assert "Retailers are adopting" in items[0]["snippet"]
    assert items[1]["url"] == "https://example.com/article-2"
