#! /usr/bin/env python3

from mistool.latex_use import install, PPath


PROJECT_NAME = "tnsseq"

DECO = " "*4

answer = input(f"{DECO}* Local installation ? [y/n] ")

if answer.lower() == "y":
    THIS_DIR = PPath( __file__ ).parent

    install(
        ppath   = THIS_DIR.parent / f"{PROJECT_NAME}",
        regpath = "file not::**.macros-x.txt"
    )

    print(f"{DECO}* Installation has been done.")
