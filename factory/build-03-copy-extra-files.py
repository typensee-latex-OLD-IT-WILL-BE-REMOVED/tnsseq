#! /usr/bin/env python3

from mistool.os_use import PPath


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR = PPath( __file__ ).parent

PROJECT_NAME     = "tnsseq"
PROJECT_PATH     = THIS_DIR.parent.parent / f"{PROJECT_NAME}"
DIR_FACTORY_PATH = PROJECT_PATH / "factory"
DIR_DOC_PATH     = PROJECT_PATH / f"{PROJECT_NAME}"

EXT_FOR_EXTRA = {
    'png'        : "PNG images",
    'tkz'        : "TikZ files",
    '[extra].tex': 'TeX "example" files',
}


DECO = " "*4


# ------------------------- #
# -- COPYING EXTRA FILES -- #
# ------------------------- #

for ext, desc in EXT_FOR_EXTRA.items():
    print(f"{DECO}* Looking for {desc}.")

    for extfile in DIR_FACTORY_PATH.walk(f"file::**.{ext}"):
        filename = extfile.stem

        if filename.endswith("-nodoc"):
            continue

        reldir = list((extfile - DIR_FACTORY_PATH).parents)

        if len(reldir) == 2:
            reldir = ""

        else:
            reldir = f"{reldir[-3] - reldir[-2]}/"


        distpath = f"{reldir}{extfile.name}"

        extfile.copy_to(
            dest     = DIR_DOC_PATH / distpath,
            safemode = False
        )

        print(f"{DECO*2}+ Copy of {extfile - DIR_FACTORY_PATH}")
