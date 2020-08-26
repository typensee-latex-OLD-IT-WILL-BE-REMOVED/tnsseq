#! /usr/bin/env python3

from mistool.latex_use import clean as latexclean
from mistool.os_use import PPath


# ----------------------- #
# -- TOOLS & CONSTANTS -- #
# ----------------------- #

THIS_DIR  = PPath( __file__ ).parent

PROJECT_NAME = "tnsseq"
PROJECT_DIR  = THIS_DIR.parent / f"{PROJECT_NAME}"


# ----------------------- #
# -- CLEAN BEFORE PUSH -- #
# ----------------------- #

for toremove in PROJECT_DIR.walk("dir::**_minted"):
    if toremove.name.startswith("_minted"):
        toremove.remove()

for toremove in THIS_DIR.walk("file::**.macros-x.txt"):
    toremove.remove()

for toremove in PROJECT_DIR.walk("file::*.macros-x.txt"):
    toremove.remove()

for toremove in THIS_DIR.walk("file::**.pdf"):
    toremove.remove()

for toremove in THIS_DIR.walk("dir::*"):
    latexclean(toremove)
