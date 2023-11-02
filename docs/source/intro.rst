cyclops-query
=============

|PyPI| |code checks| |integration tests| |docs| |codecov| |license|

``cyclops-query`` is a tool for querying relational databases using a
simple Python API. It is specifically developed to query Electronic
Health Record (EHR) databases. The tool is a wrapper around
`SQLAlchemy <https://www.sqlalchemy.org/>`__ and can be used to write
SQL-like queries in Python, including joins, conditions, groupby
aggregation and many more.

🐣 Getting Started
==================

Installing cyclops-query using pip
----------------------------------

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

🧑🏿‍💻 Developing
=============

Using poetry
------------

The development environment can be set up using
`poetry <https://python-poetry.org/docs/#installation>`__. Hence, make
sure it is installed and then run:

.. code:: bash

   python3 -m poetry install
   source $(poetry env info --path)/bin/activate

In order to install dependencies for testing (codestyle, unit tests,
integration tests), run:

.. code:: bash

   python3 -m poetry install --with test

API documentation is built using
`Sphinx <https://www.sphinx-doc.org/en/master/>`__ and can be locally
built by:

.. code:: bash

   python3 -m poetry install --with docs
   cd docs
   make html SPHINXOPTS="-D nbsphinx_allow_errors=True"

Contributing
------------

Contributing to ``cyclops-query`` is welcomed. See
`Contributing <https://vectorinstitute.github.io/cyclops-query/api/contributing.html>`__
for guidelines.

📚 `Documentation <https://vectorinstitute.github.io/cyclops-query/>`__
=======================================================================

🎓 Citation
===========

Reference to cite when you use ``cyclops-query`` in a project or a
research paper:

::

   @article {Krishnan2022.12.02.22283021,
       author = {Krishnan, Amrit and Subasri, Vallijah and McKeen, Kaden and Kore, Ali and Ogidi, Franklin and Alinoori, Mahshid and Lalani, Nadim and Dhalla, Azra and Verma, Amol and Razak, Fahad and Pandya, Deval and Dolatabadi, Elham},
       title = {CyclOps: Cyclical development towards operationalizing ML models for health},
       elocation-id = {2022.12.02.22283021},
       year = {2022},
       doi = {10.1101/2022.12.02.22283021},
       publisher = {Cold Spring Harbor Laboratory Press},
       URL = {https://www.medrxiv.org/content/early/2022/12/08/2022.12.02.22283021},
       journal = {medRxiv}
   }

.. |PyPI| image:: https://img.shields.io/pypi/v/cycquery
   :target: https://pypi.org/project/cycquery
.. |code checks| image:: https://github.com/VectorInstitute/cyclops-query/actions/workflows/code_checks.yml/badge.svg
   :target: https://github.com/VectorInstitute/cyclops-query/actions/workflows/code_checks.yml
.. |integration tests| image:: https://github.com/VectorInstitute/cyclops-query/actions/workflows/integration_tests.yml/badge.svg
   :target: https://github.com/VectorInstitute/cyclops-query/actions/workflows/integration_tests.yml
.. |docs| image:: https://github.com/VectorInstitute/cyclops-query/actions/workflows/docs_deploy.yml/badge.svg
   :target: https://github.com/VectorInstitute/cyclops-query/actions/workflows/docs_deploy.yml
.. |codecov| image:: https://codecov.io/gh/VectorInstitute/cyclops-query/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/VectorInstitute/cyclops-query
.. |license| image:: https://img.shields.io/github/license/VectorInstitute/cyclops-query.svg
   :target: https://github.com/VectorInstitute/cyclops-query/blob/main/LICENSE
