# stolen from https://github.com/pyparsing/pyparsing/blob/master/examples/simpleSQL.py

from pyparsing import (
    Word,
    delimitedList,
    Optional,
    Group,
    alphas,
    alphanums,
    Forward,
    oneOf,
    quotedString,
    infixNotation,
    opAssoc,
    CaselessKeyword,
    ParserElement,
    pyparsing_common as ppc,
)

ParserElement.enablePackrat()

# define SQL tokens
select_statement = Forward()
SELECT, FROM, WHERE, AND, OR, IN, IS, NOT, NULL = map(
    CaselessKeyword, "select from where and or in is not null".split()
)
NOT_NULL = NOT + NULL

ident = Word(alphas, alphanums).setName("identifier")
field_name = delimitedList(ident).setName("field name")
field_name.addParseAction(ppc.downcaseTokens)
field_name_list = Group(delimitedList(field_name))
sobject_name = ident.setName("sobject name")
sobject_name.addParseAction(ppc.downcaseTokens)

binop = oneOf("= != < > >= <= eq ne lt le gt ge", caseless=True)
real_num = ppc.real()
int_num = ppc.signed_integer()

field_right_value = (
    real_num | int_num | quotedString | field_name
)  # need to add support for alg expressions
where_condition = Group(
    (field_name + binop + field_right_value)
    | (field_name + IN + Group("(" + delimitedList(field_right_value) + ")"))
    | (field_name + IS + (NULL | NOT_NULL))
)

where_expression = infixNotation(
    where_condition,
    [
        (NOT, 1, opAssoc.RIGHT),
        (AND, 2, opAssoc.LEFT),
        (OR, 2, opAssoc.LEFT),
    ],
)

# define the grammar
select_statement <<= (
    SELECT
    + field_name_list("fields")
    + FROM
    + sobject_name("sobject")
    + Optional(Group(WHERE + where_expression), "")("where")
)

soql = select_statement


def parse(soql_query: str):
    return soql.parseString(soql_query)
