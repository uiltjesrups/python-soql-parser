def parse(soql):
    pass


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

ident = Word(alphas, alphanums + "_$").setName("identifier")
field_name = delimitedList(ident, ".", combine=True).setName("field name")
field_name.addParseAction(ppc.upcaseTokens)
field_name_list = Group(delimitedList(field_name))
sobject_name = delimitedList(ident, ".", combine=True).setName("sobject name")
sobject_name.addParseAction(ppc.upcaseTokens)
sobject_name_list = Group(delimitedList(sobject_name))

binop = oneOf("= != < > >= <= eq ne lt le gt ge", caseless=True)
real_num = ppc.real()
int_num = ppc.signed_integer()

field_right_value = (
    real_num | int_num | quotedString | field_name
)  # need to add support for alg expressions
whereCondition = Group(
    (field_name + binop + field_right_value)
    | (field_name + IN + Group("(" + delimitedList(field_right_value) + ")"))
    | (field_name + IN + Group("(" + select_statement + ")"))
    | (field_name + IS + (NULL | NOT_NULL))
)

where_expression = infixNotation(
    whereCondition,
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
    + sobject_name_list("sobjects")
    + Optional(Group(WHERE + where_expression), "")("where")
)

soql = select_statement


if __name__ == "__main__":
    soql.runTests(
        """\
        # multiple sobjects
        SELECT A from XYZZY, ABC
        # dotted sobject name
        select A from SYS.XYZZY
        Select A from Sys.dual
        Select A,B,C from Sys.dual
        Select A, B, C from Sys.dual, Sobject2
        # FAIL - invalid SELECT keyword
        Xelect A, B, C from Sys.dual
        # FAIL - invalid FROM keyword
        Select A, B, C frox Sys.dual
        # FAIL - incomplete statement
        Select
        # FAIL - incomplete statement
        Select A from
        # FAIL - invalid field
        Select &&& frox Sys.dual
        # where clause
        Select A from Sys.dual where a in ('RED','GREEN','BLUE')
        # compound where clause
        Select A from Sys.dual where a in ('RED','GREEN','BLUE') and b in (10,20,30)
        # where clause with comparison operator
        Select A,b from sobject1,sobject2 where sobject1.id eq sobject2.id
        """
    )