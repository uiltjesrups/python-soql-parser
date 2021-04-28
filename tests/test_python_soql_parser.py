import pytest

from python_soql_parser import parse


@pytest.mark.parametrize(
    "query,sobject,fields",
    [
        ("Select Id FROM Contact", "Contact", ["Id"]),
        ("SElECT Id, Name from Contact", "Contact", ["Id", "Name"]),
        (
            "SElECT Id, SuperTitle__c from Custom_Object__c",
            "Custom_Object__c",
            ["Id", "SuperTitle__c"],
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
            "Contact",
            ["Id"],
            [["Id", "!=", "null"]],
        ),
        (
            "SELECT Id, Name FROM Contact WHERE (Id = '123' AND Name = null)",
            "Contact",
            ["Id", "Name"],
            [[["Id", "=", "'123'"], "and", ["Name", "=", "null"]]],
        ),
        (
            "SELECT Id, Name, Title FROM Contact WHERE (Id = '123' AND Name = null) OR (Title != 'CEO')",
            "Contact",
            ["Id", "Name", "Title"],
            [
                [
                    [["Id", "=", "'123'"], "and", ["Name", "=", "null"]],
                    "or",
                    ["Title", "!=", "'CEO'"],
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
        ("Select Id FROM Contact LIMIT 1", "Contact", ["Id"], [1]),
        ("Select Id FROM Contact limit 99", "Contact", ["Id"], [99]),
    ],
)
def test_query_with_limit(query, sobject, fields, limit):
    parsed = parse(query)
    assert parsed["sobject"] == sobject
    assert parsed["fields"].asList() == fields
    assert parsed["limit"].asList() == limit


@pytest.mark.parametrize(
    "query,sobject,fields,order",
    [
        (
            "Select Id FROM Contact ORDER BY Id DESC",
            "Contact",
            ["Id"],
            [[["Id", "desc"]]],
        ),
        (
            "Select Id, Name, Title FROM Contact ORDER BY Id DESC, Name ASC, Title DESC",
            "Contact",
            ["Id", "Name", "Title"],
            [[["Id", "desc"], ["Name", "asc"], ["Title", "desc"]]],
        ),
    ],
)
def test_query_with_order_by(query, sobject, fields, order):
    parsed = parse(query)
    assert parsed["sobject"] == sobject
    assert parsed["fields"].asList() == fields
    assert parsed["order_by"].asList() == order
