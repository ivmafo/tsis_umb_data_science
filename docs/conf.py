import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'TSIS UMB Data Science'
copyright = '2025, Iván Forero'
author = 'Iván Forero'

# Configuración del idioma
language = 'es'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.coverage',
    'sphinx.ext.intersphinx',
]

html_theme = 'sphinx_rtd_theme'
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']