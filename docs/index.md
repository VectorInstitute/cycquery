# cycquery

[![PyPI](https://img.shields.io/pypi/v/cycquery)](https://pypi.org/project/cycquery)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cycquery)
[![code checks](https://github.com/VectorInstitute/cycquery/actions/workflows/code_checks.yml/badge.svg)](https://github.com/VectorInstitute/cycquery/actions/workflows/code_checks.yml)
[![integration tests](https://github.com/VectorInstitute/cycquery/actions/workflows/integration_tests.yml/badge.svg)](https://github.com/VectorInstitute/cycquery/actions/workflows/integration_tests.yml)
[![docs](https://github.com/VectorInstitute/cycquery/actions/workflows/docs.yml/badge.svg)](https://github.com/VectorInstitute/cycquery/actions/workflows/docs.yml)
[![codecov](https://codecov.io/gh/VectorInstitute/cycquery/branch/main/graph/badge.svg)](https://codecov.io/gh/VectorInstitute/cycquery)

`cycquery` is a tool for querying relational databases using a simple Python API.
It is specifically developed to query Electronic Health Record (EHR) databases.
The tool is a wrapper around [SQLAlchemy](https://www.sqlalchemy.org/) and can be used
to write SQL-like queries in Python, including joins, conditions, groupby aggregation
and many more.

## Getting Started

### Installing cycquery using pip

```bash
python3 -m pip install cycquery
```

### Query postgresql database

```python
from cycquery import DatasetQuerier
import cycquery.ops as qo


querier = DatasetQuerier(
    dbms="postgresql",
    port=5432,
    host="localhost",
    database="dbname",
    user="usename",
    password="password",
)
# List all tables.
querier.list_tables()

# Get some table.
table = querier.schema.sometable()
# Filter based on some condition (e.g. substring match).
table = table.ops(qo.ConditionSubstring("col1", "substr"))
# Run query to get data as a pandas dataframe.
df = table.run()

# Create a sequential list of operations to perform on the query.
ops = qo.Sequential(
    qo.ConditionIn("col2", [1, 2]),
    qo.DropNulls("col3"),
    qo.Distinct("col1")
)
table = table.ops(ops)
# Run query to get data as a pandas dataframe.
df = table.run()
```

Please check out the [user guide](user_guide.md) for more detailed information on
setting up a development environment, building documentation, and contributing.
For API reference, see the [API Reference](api.md) page.
