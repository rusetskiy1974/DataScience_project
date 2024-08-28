# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sys
import os
from unittest.mock import MagicMock


sys.path.insert(0, os.path.abspath('../..'))


class Mock(MagicMock):
    @classmethod
    def __getattr__(cls, name):
        return MagicMock()

MOCK_MODULES = ['tensorflow', 'tensorflow.lite', 'app.data_science.detector', 'app.data_science.character_recogniser']
sys.modules.update((mod_name, Mock()) for mod_name in MOCK_MODULES)

sys.path.insert(0, os.path.abspath('../stubs'))

project = 'DataScience_project'
copyright = '2024, Group5'
author = 'Group5'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
autodoc_mock_imports = ['tensorflow', 'app.data_science.detector', 'app.data_science.character_recogniser']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'agogo'
html_static_path = ['_static']
