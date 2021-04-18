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
column_name = delimitedList(ident, ".", combine=True).setName("column name")
column_name.addParseAction(ppc.upcaseTokens)
column_name_list = Group(delimitedList(column_name))
table_name = delimitedList(ident, ".", combine=True).setName("table name")
table_name.addParseAction(ppc.upcaseTokens)
table_name_list = Group(delimitedList(table_name))

binop = oneOf("= != < > >= <= eq ne lt le gt ge", caseless=True)
real_num = ppc.real()
int_num = ppc.signed_integer()

column_right_value = (
    real_num | int_num | quotedString | column_name
)  # need to add support for alg expressions
whereCondition = Group(
    (column_name + binop + column_right_value)
    | (column_name + IN + Group("(" + delimitedList(column_right_value) + ")"))
    | (column_name + IN + Group("(" + select_statement + ")"))
    | (column_name + IS + (NULL | NOT_NULL))
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
    + ("*" | column_name_list)("columns")
    + FROM
    + table_name_list("tables")
    + Optional(Group(WHERE + where_expression), "")("where")
)

soql = select_statement


if __name__ == "__main__":
    soql.runTests(
        """\
        # multiple tables
        SELECT * from XYZZY, ABC
        # dotted table name
        select * from SYS.XYZZY
        Select A from Sys.dual
        Select A,B,C from Sys.dual
        Select A, B, C from Sys.dual, Table2
        # FAIL - invalid SELECT keyword
        Xelect A, B, C from Sys.dual
        # FAIL - invalid FROM keyword
        Select A, B, C frox Sys.dual
        # FAIL - incomplete statement
        Select
        # FAIL - incomplete statement
        Select * from
        # FAIL - invalid column
        Select &&& frox Sys.dual
        # where clause
        Select A from Sys.dual where a in ('RED','GREEN','BLUE')
        # compound where clause
        Select A from Sys.dual where a in ('RED','GREEN','BLUE') and b in (10,20,30)
        # where clause with comparison operator
        Select A,b from table1,table2 where table1.id eq table2.id
        """
    )