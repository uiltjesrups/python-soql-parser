import pytest

from python_soql_parser import parse


@pytest.mark.parametrize(
    "fields_string,expected",
    [("Id", ["id"]), ("id, NAME", ["id", "name"])],
)
def test_basic_query(fields_string, expected):
    parsed = parse(f"SELECT {fields_string} FROM Contact")
    assert parsed["sobject"] == "Contact"
    assert parsed["fields"].asList() == expected
