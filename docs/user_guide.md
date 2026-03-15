# User Guide

## Installation

### Installing cycquery using pip

```bash
python3 -m pip install cycquery
```

### Development setup using uv

The development environment can be set up using
[uv](https://docs.astral.sh/uv/). Hence, make sure it is installed and then run:

```bash
uv sync
source .venv/bin/activate
```

In order to install dependencies for testing (codestyle, unit tests, integration tests),
run:

```bash
uv sync --dev
source .venv/bin/activate
```

## Documentation

This project uses [MkDocs](https://www.mkdocs.org/) with the
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme.

To build the documentation locally, install the documentation dependencies:

```bash
uv sync --all-extras --group docs
```

Then build or serve the docs:

```bash
# Build
uv run mkdocs build

# Serve locally with live reload at http://127.0.0.1:8000
uv run mkdocs serve
```

### GitHub Pages Setup

To serve documentation on GitHub Pages:

1. Go to your repository's **Settings** tab
2. Navigate to **Pages** in the left sidebar
3. Under **Source**, select **Deploy from a branch**
4. Choose the **gh-pages** branch and **/ (root)** folder
5. Click **Save**

The documentation is automatically built and deployed to GitHub Pages whenever
changes are pushed to the main branch (via the `.github/workflows/docs.yml` workflow).

## Tutorials

The cycquery tool allows you to query EHR databases using a Python API that
communicates with PostgreSQL databases. It is a wrapper around the SQLAlchemy ORM
and uses SQLAlchemy query objects and functions to build queries.

The following tutorials are available in the
[tutorials directory](https://github.com/VectorInstitute/cycquery/tree/main/docs/source/tutorials)
of the repository:

- **MIMIC-III** — Querying the MIMIC-III EHR database
- **MIMIC-IV** — Querying the MIMIC-IV EHR database
- **eICU** — Querying the eICU Collaborative Research Database
- **OMOP** — Querying OMOP CDM databases
- **Gemini** — Querying the Gemini database

## Contributing

Thanks for your interest in contributing to cycquery!

To submit PRs, please fill out the PR template along with the PR. If the PR
fixes an issue, don't forget to link the PR to the issue!

### Pre-commit hooks

Once the python virtual environment is set up, you can run pre-commit hooks using:

```bash
pre-commit run --all-files
```

### Coding guidelines

For code style, we recommend the
[Google style guide](https://google.github.io/styleguide/pyguide.html).

Pre-commit hooks apply the
[black](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html)
code formatting.

For docstrings we use
[numpy format](https://numpydoc.readthedocs.io/en/latest/format.html).

We use [ruff](https://github.com/astral-sh/ruff) for further static code analysis.
The pre-commit hooks show errors which you need to fix before submitting a PR.

We use type hints in our code which is then checked using
[mypy](https://mypy.readthedocs.io/en/stable/).

## GitHub Actions

The repository includes several GitHub Actions workflows:

- **[code checks](https://github.com/VectorInstitute/cycquery/actions/workflows/code_checks.yml)**: Static code analysis, code formatting and unit tests
- **[documentation](https://github.com/VectorInstitute/cycquery/actions/workflows/docs.yml)**: Project documentation build and deploy
- **[integration tests](https://github.com/VectorInstitute/cycquery/actions/workflows/integration_tests.yml)**: Integration tests
- **[publish](https://github.com/VectorInstitute/cycquery/actions/workflows/publish.yml)**: Publishing the python package to PyPI

!!! warning "codecov"
    The [codecov](https://app.codecov.io/github/VectorInstitute) tool is subscribed
    under the free tier which makes it usable only for public open-source repos.
    Hence, if you would like to develop in a private repo, it is recommended to
    remove the codecov actions from the github workflow files.
