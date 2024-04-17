cycquery
--------------------------------------------------------------------------------

[![PyPI](https://img.shields.io/pypi/v/cycquery)](https://pypi.org/project/cycquery)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cycquery)
[![code checks](https://github.com/VectorInstitute/cycquery/actions/workflows/code_checks.yml/badge.svg)](https://github.com/VectorInstitute/cycquery/actions/workflows/code_checks.yml)
[![integration tests](https://github.com/VectorInstitute/cycquery/actions/workflows/integration_tests.yml/badge.svg)](https://github.com/VectorInstitute/cycquery/actions/workflows/integration_tests.yml)
[![docs](https://github.com/VectorInstitute/cycquery/actions/workflows/docs_deploy.yml/badge.svg)](https://github.com/VectorInstitute/cycquery/actions/workflows/docs_deploy.yml)
[![codecov](https://codecov.io/gh/VectorInstitute/cycquery/branch/main/graph/badge.svg)](https://codecov.io/gh/VectorInstitute/cycquery)
[![license](https://img.shields.io/github/license/VectorInstitute/cycquery.svg)](https://github.com/VectorInstitute/cycquery/blob/main/LICENSE)

``cycquery`` is a tool for querying relational databases using a simple Python API. It is specifically developed to query
Electronic Health Record (EHR) databases. The tool is a wrapper around [SQLAlchemy](https://www.sqlalchemy.org/) and can be used
to write SQL-like queries in Python, including joins, conditions, groupby aggregation and many more.

## 🐣 Getting Started

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

## 🧑🏿‍💻 Developing

### Using poetry

The development environment can be set up using
[poetry](https://python-poetry.org/docs/#installation). Hence, make sure it is
installed and then run:


```bash
python3 -m poetry install
source $(poetry env info --path)/bin/activate
```

In order to install dependencies for testing (codestyle, unit tests, integration tests),
run:

```bash
python3 -m poetry install --with test
```

API documentation is built using [Sphinx](https://www.sphinx-doc.org/en/master/) and
can be locally built by:

```bash
python3 -m poetry install --with docs
cd docs
make html SPHINXOPTS="-D nbsphinx_allow_errors=True"
```

### Contributing

Contributing to ``cycquery`` is welcomed.
See [Contributing](https://vectorinstitute.github.io/cycquery/api/contributing.html) for
guidelines.


## 📚 [Documentation](https://vectorinstitute.github.io/cycquery/)
