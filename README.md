# Installation

`pip install python-soql-parser`

or, with poetry

`poetry add python-soql-parser`

# Usage

```python
from python_sql_parser import parse


parse_result = parse("SELECT Id FROM Account")
```

where `parse_result` is a [ParseResults](https://pyparsing-docs.readthedocs.io/en/latest/HowToUsePyparsing.html#parseresults) object from [pyparsing](https://github.com/pyparsing/pyparsing/).

# Notable unsupported features

- Related attributes (e.g., `SELECT Id, Account.Name FROM Contact)
- Subqueries (e.g., `SELECT Name, (SELECT LastName FROM Contacts) FROM Account`)
- Aggregate queries
- SOQL specific WHERE-clause tokens (e.g., LAST_N_DAYS:<integer>)

# Contributing

A lot of work remains to be done. If you want to contribute, just open a PR! (and add a test for your new feature)

## Setting up locally

First instally (poetry)[https://python-poetry.org/]. Afterwards, to install the dependencies, run

```
poetry install
```

## Running the tests

Simply execute

```
pytest
```
