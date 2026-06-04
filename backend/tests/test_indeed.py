from scrapers.indeed import _parse_salary, _parse_job_type


def test_parse_salary_none():
    assert _parse_salary(None) is None


def test_parse_salary_value():
    assert _parse_salary("  $50k - $70k  ") == "$50k - $70k"


def test_parse_job_type_full_time():
    assert _parse_job_type("Full-time") == "Full-time"


def test_parse_job_type_none():
    assert _parse_job_type(None) is None


def test_parse_job_type_part_time():
    assert _parse_job_type("Part-time") == "Part-time"


def test_parse_job_type_contract():
    assert _parse_job_type("Contract") == "Contract"
