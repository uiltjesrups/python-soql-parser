# stolen from https://github.com/pyparsing/pyparsing/blob/master/examples/simpleSQL.py

from typing import TypedDict, Any

from pyparsing import (
    CaselessKeyword,
    Forward,
    Group,
    Optional,
    ParserElement,
    PrecededBy,
    Suppress,
    Word,
    alphanums,
    alphas,
    delimitedList,
    infixNotation,
    oneOf,
    opAssoc,
    pyparsing_common,
    quotedString,
)

ParserElement.enablePackrat()

# define SQL tokens
select_statement = Forward()
SELECT, FROM, WHERE, AND, OR, IN, NULL, LIMIT = map(
    CaselessKeyword, "select from where and or in null limit".split()
)

identifier = Word(alphas, alphanums).setName("identifier")
field_name = delimitedList(identifier).setName("field name")
field_name.addParseAction(pyparsing_common.downcaseTokens)
field_name_list = Group(delimitedList(field_name))
sobject_name = identifier.setName("sobject name")
sobject_name.addParseAction(pyparsing_common.downcaseTokens)

binop = oneOf("= != < > >= <=")
real_num = pyparsing_common.real()
int_num = pyparsing_common.signed_integer()

field_right_value = real_num | int_num | quotedString | field_name
where_condition = Group(
    (field_name + binop + field_right_value)
    | (field_name + IN + Group("(" + delimitedList(field_right_value) + ")"))
)

where_expression = infixNotation(
    where_condition,
    [
        (AND, 2, opAssoc.LEFT),
        (OR, 2, opAssoc.LEFT),
    ],
)

where_clause = Optional(Suppress(WHERE) + where_expression, None)

limit_clause = Optional(Suppress(LIMIT) + int_num, None)

# define the grammar
select_statement <<= (
    SELECT
    + field_name_list("fields")
    + FROM
    + sobject_name("sobject")
    + where_clause("where")
    + limit_clause("limit")
)

soql = select_statement


class SoqlQuery(TypedDict):
    # TODO: type the `Any`s
    fields: Any
    sobject: str
    where: Any
    limit: Any


def parse(soql_query: str) -> SoqlQuery:
    return soql.parseString(soql_query)
