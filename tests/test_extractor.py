from lead_enrichment.crawler import Page, clean_html
from lead_enrichment.extractor import local_extract


def test_clean_html_removes_non_content_nodes():
    title, text = clean_html("<html><title>Acme</title><nav>Menu</nav><main>Hello <b>world</b></main><script>x</script></html>", 100)
    assert title == "Acme"
    assert text == "Hello world"


def test_local_extract_is_structured_and_resilient():
    result = local_extract(
        "acme.com",
        [Page("https://acme.com", "Acme | Home", "Contact us at hello@acme.com express@4.18.2")],
    )
    assert result.company_name == "Acme"
    assert result.contact_emails == ["hello@acme.com"]
    assert result.crawl_status == "success"


def test_failed_pages_do_not_raise():
    result = local_extract("blocked.example", [Page("https://blocked.example", "", "", error="timeout")])
    assert result.crawl_status == "failed"
    assert result.error == "timeout"