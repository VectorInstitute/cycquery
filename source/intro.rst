cycquery
========

|PyPI| |PyPI - Python Version| |code checks| |integration tests| |docs|
|codecov|

``cycquery`` is a tool for querying relational databases using a simple
Python API. It is specifically developed to query Electronic Health
Record (EHR) databases. The tool is a wrapper around
`SQLAlchemy <https://www.sqlalchemy.org/>`__ and can be used to write
SQL-like queries in Python, including joins, conditions, groupby
aggregation and many more.

🐣 Getting Started
==================

Installing cycquery using pip
-----------------------------

.. code:: bash

   python3 -m pip install cycquery

Query postgresql database
-------------------------

.. code:: python

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

=========================

Using uv
--------

The development environment can be set up using
`uv <https://docs.astral.sh/uv/>`__. Hence, make sure it is installed
and then run:

.. code:: bash

   uv sync
   source .venv/bin/activate

In order to install dependencies for testing (codestyle, unit tests,
integration tests), run:

.. code:: bash

   uv sync --dev
   source .venv/bin/activate

API documentation is built using
`Sphinx <https://www.sphinx-doc.org/en/master/>`__ and can be locally
built by:

.. code:: bash

   uv sync --group docs
   cd docs
   make html SPHINXOPTS="-D nbsphinx_allow_errors=True"

Contributing
------------

Contributing to ``cycquery`` is welcomed. See
`Contributing <https://vectorinstitute.github.io/cycquery/api/contributing.html>`__
for guidelines.

📚 `Documentation <https://vectorinstitute.github.io/cycquery/>`__
==================================================================

.. |PyPI| image:: https://img.shields.io/pypi/v/cycquery
   :target: https://pypi.org/project/cycquery
.. |PyPI - Python Version| image:: https://img.shields.io/pypi/pyversions/cycquery
.. |code checks| image:: https://github.com/VectorInstitute/cycquery/actions/workflows/code_checks.yml/badge.svg
   :target: https://github.com/VectorInstitute/cycquery/actions/workflows/code_checks.yml
.. |integration tests| image:: https://github.com/VectorInstitute/cycquery/actions/workflows/integration_tests.yml/badge.svg
   :target: https://github.com/VectorInstitute/cycquery/actions/workflows/integration_tests.yml
.. |docs| image:: https://github.com/VectorInstitute/cycquery/actions/workflows/docs_deploy.yml/badge.svg
   :target: https://github.com/VectorInstitute/cycquery/actions/workflows/docs_deploy.yml
.. |codecov| image:: https://codecov.io/gh/VectorInstitute/cycquery/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/VectorInstitute/cycquery
