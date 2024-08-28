import sys
import os

sys.path.append(os.path.abspath('..'))
project = 'DataScience_project'
copyright = '2024, Group5'
author = 'Group5'

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'nature'
html_static_path = ['_static']
