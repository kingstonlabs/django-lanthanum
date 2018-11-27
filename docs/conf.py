# -*- coding: utf-8 -*-
import sys
import os

project_path = os.path.dirname(
    (os.path.dirname(os.path.realpath(__file__)))
)

# Add the app to path
sys.path.insert(0, project_path)


# -- General configuration ------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']

source_suffix = '.rst'

source_encoding = 'utf-8-sig'

master_doc = 'index'

project = 'Django Lanthanum'
copyright = '2018, Kingston Labs'
author = 'Kingston Labs'

version = '0.1'
release = '0.1.0'

language = 'en'

exclude_patterns = []

pygments_style = 'sphinx'

todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

html_theme = "sphinx_rtd_theme"

# Output file base name for HTML help builder.
htmlhelp_basename = 'DjangoLanthanumDoc'
