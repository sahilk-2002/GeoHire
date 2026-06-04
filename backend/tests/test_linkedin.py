from scrapers.linkedin import scrape_linkedin


def test_scrape_linkedin_returns_list():
    results = scrape_linkedin("San Francisco, CA", "software engineer")
    assert isinstance(results, list)


def test_scrape_linkedin_job_has_required_fields():
    results = scrape_linkedin("San Francisco, CA", "software engineer")
    if results:
        job = results[0]
        assert "title" in job
        assert "company" in job
        assert "location" in job
        assert "description" in job
        assert "source" in job
        assert job["source"] == "linkedin"


def test_scrape_linkedin_invalid_location():
    results = scrape_linkedin("", "test")
    assert results == []
