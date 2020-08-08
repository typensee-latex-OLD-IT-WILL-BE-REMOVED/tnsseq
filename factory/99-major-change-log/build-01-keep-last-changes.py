
#! /usr/bin/env python3

from datetime import datetime
from collections import defaultdict

from mistool.os_use import PPath


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR    = PPath(__file__).parent
CHANGES_DIR = THIS_DIR / 'changes'

DECO = " "*4

TOO_OLD_NB_OF_DAYS = 365
LAST_DATE          = None


# ----------- #
# -- TOOLS -- #
# ----------- #

def istooold(ppath):
    global LAST_DATE

    thisdate = datetime.strptime(
        f"{ppath.parent.stem}-{ppath.stem}",
        '%Y-%m-%d'
    )

    delta = LAST_DATE - thisdate

    return TOO_OLD_NB_OF_DAYS <= delta.days


def renamethis(ppath):
    newppath = ppath.parent / f"_{ppath.name}"
    ppath.rename(newppath)

    return newppath


def printrenaming(ppath, showparent = True):
    if showparent:
        parent = f"{ppath.parent.name}/"

    else:
        parent = ""

    print(
        f"{DECO}* Renaming << {parent}{ppath.name} >> "
        f"to << {parent}_{ppath.name} >>"
    )


# ------------------- #
# -- CHANGES SHOWN -- #
# ------------------- #

allppaths = []

for ppath in CHANGES_DIR.walk("file::**.tex"):
    if ppath.parent.stem.startswith("_") \
    or ppath.stem.startswith("_"):
        continue

    allppaths.append(ppath)


# ------------------ #
# -- LAST VERSION -- #
# ------------------ #

allppaths.sort()

lastppath = allppaths[-1]
LAST_DATE = datetime.strptime(
    f"{lastppath.parent.stem}-{lastppath.stem}",
    '%Y-%m-%d'
)


# ----------------------------- #
# -- REMOVE THE TOO OLD ONES -- #
# ----------------------------- #

foldertokeep = defaultdict(bool)

for i, ppath in enumerate(allppaths[:-1]):
    if istooold(ppath):
        printrenaming(ppath)

        allppaths[i] = renamethis(ppath)
        foldertokeep[ppath.parent]


# --------------------- #
# -- FOLDERS TOO OLD -- #
# --------------------- #

for ppath in allppaths[:-1]:
    if ppath.parent in foldertokeep \
    and not ppath.stem.startswith("_"):
        foldertokeep[ppath.parent] = True


for folder, tokeep in foldertokeep.items():
    if not tokeep:
        printrenaming(folder, False)

        renamethis(folder)
