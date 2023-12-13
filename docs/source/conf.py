"""Configuration file for the Sphinx documentation builder."""

# pylint: disable-all

# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys


sys.path.insert(0, os.path.abspath("../../cycquery"))


# -- Project information -----------------------------------------------------

project = "cyclops-query"
copyright = "2022, Vector AI Engineering"  # noqa: A001
author = "Vector AI Engineering"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "myst_parser",
    "sphinx_copybutton",
    "nbsphinx",
    "IPython.sphinxext.ipython_console_highlighting",
]
autosummary_generate = True
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_attr_annotations = True
add_module_names = False
autoclass_content = "both"
autodoc_inherit_docstrings = True
set_type_checking_flag = True
autosectionlabel_prefix_document = True
copybutton_prompt_text = r">>> |\.\.\. "
copybutton_prompt_is_regexp = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3.9/", None),
    "numpy": ("http://docs.scipy.org/doc/numpy/", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
    "sqlalchemy": ("https://docs.sqlalchemy.org", None),
    "sklearn": ("https://scikit-learn.org/stable/", None),
    "dask": ("https://docs.dask.org/en/stable/", None),
    "torch": ("https://pytorch.org/docs/stable/", None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["**.ipynb_checkpoints"]
source_suffix = [".rst", ".md"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "theme"
html_theme_path = ["."]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]