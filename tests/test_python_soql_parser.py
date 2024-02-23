import pytest
from pyparsing import ParseException

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
            "SELECT IsDeleted FROM Contact WHERE IsDeleted != true",
            "Contact",
            ["IsDeleted"],
            [["IsDeleted", "!=", "true"]],
        ),
        (
            "SELECT IsDeleted FROM Contact WHERE IsDeleted = false",
            "Contact",
            ["IsDeleted"],
            [["IsDeleted", "=", "false"]],
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
    "query,sobject,fields,offset",
    [
        ("Select Id FROM Contact OFFSET 1", "Contact", ["Id"], [1]),
        ("Select Id FROM Contact OFFSET 99", "Contact", ["Id"], [99]),
    ],
)
def test_query_with_offset(query, sobject, fields, offset):
    parsed = parse(query)
    assert parsed["sobject"] == sobject
    assert parsed["fields"].asList() == fields
    assert parsed["offset"].asList() == offset


@pytest.mark.parametrize(
    "query,sobject,fields,limit,offset",
    [
        ("Select Id FROM Contact LIMIT 10 OFFSET 1", "Contact", ["Id"], [10], [1]),
        ("Select Id FROM Contact LIMIT 1 OFFSET 99", "Contact", ["Id"], [1], [99]),
    ],
)
def test_query_with_limit_offset(query, sobject, fields, limit, offset):
    parsed = parse(query)
    assert parsed["sobject"] == sobject
    assert parsed["fields"].asList() == fields
    assert parsed["limit"].asList() == limit
    assert parsed["offset"].asList() == offset


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


@pytest.mark.parametrize(
    "query,sobject,fields",
    [
        (
            "Select Id, Account.Id FROM Contact",
            "Contact",
            ["Id", "Account.Id"],
        ),
        (
            "Select Account.Id, Id FROM Contact",
            "Contact",
            ["Account.Id", "Id"],
        ),
    ],
)
def test_query_with_parent_attribute(query, sobject, fields):
    parsed = parse(query)
    assert parsed["sobject"] == sobject
    assert parsed["fields"].asList() == fields


@pytest.mark.parametrize(
    "query, where",
    [
        (
            "Select Id From Account Where CreatedDate > 2022-06-03T20:42:04.345064",
            [["CreatedDate", ">", "2022-06-03T20:42:04.345064"]],
        ),
        (
            "Select Id From Account Where CreatedDate > 2022-06-03T20:42:04.345064 and CreatedDate < 2022-08-03T20:42:04.345064",
            [
                [
                    ["CreatedDate", ">", "2022-06-03T20:42:04.345064"],
                    "and",
                    ["CreatedDate", "<", "2022-08-03T20:42:04.345064"],
                ]
            ],
        ),
        (
            "Select Id From Account Where IsDeleted != true and Amount >= 1000 and "
            "Total != 0.0 and Description = 'Something' and "
            "CreatedDate > 2022-06-03T20:42:04.345064 and CreatedDate < 2022-08-03T20:42:04.345064",
            [
                [
                    ["IsDeleted", "!=", "true"],
                    "and",
                    ["Amount", ">=", 1000],
                    "and",
                    ["Total", "!=", 0.0],
                    "and",
                    ["Description", "=", "'Something'"],
                    "and",
                    ["CreatedDate", ">", "2022-06-03T20:42:04.345064"],
                    "and",
                    ["CreatedDate", "<", "2022-08-03T20:42:04.345064"],
                ]
            ],
        ),
    ],
)
def test_query_datetime(query, where):
    parsed = parse(query)
    assert parsed["where"].asList() == where


@pytest.mark.parametrize(
    "query,result",
    [
        ("", 'Expected "select"'),
        ("select Id", 'Expected "from"'),
        ("select Id from", "Expected sobject name"),
        ("select Id from Obj where", "Expected end of text, found 'w'"),
    ],
)
def test_exceptions(query, result):
    with pytest.raises(Exception) as e:
        parse(query)
    assert str(e.value).startswith(result)
