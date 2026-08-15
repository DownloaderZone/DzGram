import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

with open(os.path.join(os.path.dirname(__file__), "../../pyrogram/__init__.py")) as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"')
            break

project = "DzGram"
copyright = "2017-present Dan, Downloader Zone"
author = "Dan, Downloader Zone"
release = version

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
    "sphinx_design",
]

autodoc_mock_imports = [
    "warpcrypto",
    "tgcrypto",
    "cryptg",
    "pysocks",
    "uvloop",
]

autosummary_generate = True

napoleon_use_rtype = False
napoleon_use_param = False

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
]

html_theme = "furo"
html_title = "DzGram"
html_baseurl = "https://downloaderzone.github.io/DzGram/"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

autodoc_default_options = {
    "member-order": "bysource",
    "undoc-members": False,
}

suppress_warnings = [
    "image.not_readable",
    "ref.python",
]
