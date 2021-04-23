import pytest

from python_soql_parser import parse


@pytest.mark.parametrize(
    "query,sobject,fields",
    [
        ("Select Id FROM Contact", "contact", ["id"]),
        ("SElECT id, NAME from CONTACT", "contact", ["id", "name"]),
        (
            "SElECT Id, SuperTitle__c from Custom_Object__c",
            "custom_object__c",
            ["id", "supertitle__c"],
        ),
    ],
)
def test_basic_query(query, sobject, fields):
    parsed = parse(query)
    assert parsed["sobject"] == sobject
    assert parsed["fields"].asList() == fields
    # Should be no where clause
    assert parsed["where"].asList() == []


@pytest.mark.parametrize(
    "query,sobject,fields,where",
    [
        (
            "SELECT Id FROM Contact WHERE Id != null",
            "contact",
            ["id"],
            [["id", "!=", "null"]],
        ),
        (
            "SELECT Id, Name FROM Contact WHERE (Id = '123' AND Name = null)",
            "contact",
            ["id", "name"],
            [[["id", "=", "'123'"], "and", ["name", "=", "null"]]],
        ),
        (
            "SELECT Id, Name, Title FROM Contact WHERE (Id = '123' AND Name = null) OR (Title != 'CEO')",
            "contact",
            ["id", "name", "title"],
            [
                [
                    [["id", "=", "'123'"], "and", ["name", "=", "null"]],
                    "or",
                    ["title", "!=", "'CEO'"],
                ],
            ],
        ),
    ],
)
def test_where_query(query, sobject, fields, where):
    parsed = parse(query)
    assert parsed["sobject"] == sobject
    assert parsed["fields"].asList() == fields
    assert parsed["where"].asList() == where


@pytest.mark.parametrize(
    "query,sobject,fields,limit",
    [
        ("Select Id FROM Contact LIMIT 1", "contact", ["id"], [1]),
        ("Select Id FROM Contact limit 99", "contact", ["id"], [99]),
    ],
)
def test_query_with_limit(query, sobject, fields, limit):
    parsed = parse(query)
    assert parsed["sobject"] == sobject
    assert parsed["fields"].asList() == fields
    assert parsed["limit"].asList() == limit
