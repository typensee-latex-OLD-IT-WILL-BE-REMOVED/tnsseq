
#! /usr/bin/env python3

from mistool.os_use import PPath
from mistool.string_use import between, joinand


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR    = PPath(__file__).parent
CHANGES_DIR = THIS_DIR / 'changes'

CHANGE_LOG_TEX_FILE   = THIS_DIR / "01-change-log[fr].tex"
MAIN_DOC_LOG_TEX_FILE = THIS_DIR.parent / "config" / "doc[fr].tex"

DECO_SPACE = " "*4
DECO_SEP   = """
% ------------------------ %

"""

# ------------------- #
# -- CHANGES SHOWN -- #
# ------------------- #

allppaths = []

for ppath in CHANGES_DIR.walk("file::**.tex"):
    if ppath.parent.stem.startswith("_") \
    or ppath.stem.startswith("_"):
        continue

    allppaths.append(ppath)


# ---------------------------------- #
# -- LAST VERSION : NUMBER & DATE -- #
# ---------------------------------- #

# We have to sort the ppaths found.
allppaths.sort()

lastppath = allppaths[-1]
lastdate  = f"{lastppath.parent.stem}-{lastppath.stem}"


with lastppath.open(
    mode = "r",
    encoding = "utf-8"
) as f:
    for line in f:
        _, lastversion = line.split("verb+", maxsplit = 1)
        lastversion, _ = lastversion.split("+", maxsplit = 1)
        break


# ------------------------------------ #
# -- UPDATING THE CHANGE LATEX CODE -- #
# ------------------------------------ #

# We have to revrese sort the ppaths found.
allppaths.sort(reverse = True)

with CHANGE_LOG_TEX_FILE.open(
    mode     = "r",
    encoding = "utf-8"
) as f:
    text_start, _, text_end = between(
        text = f.read(),
        seps = [
            "% Changes shown - START",
            "% Changes shown - END"
        ],
        keepseps = True
    )

content = ["\n"*2]

for ppath in allppaths:
    with ppath.open(
        mode     = "r",
        encoding = "utf-8"
    ) as f:
        firstline = True

        for line in f.readlines():
            if firstline:
                line = f"\\medskip\n{DECO_SPACE}" \
                     + f"\\item[{ppath.parent.stem}-{ppath.stem}] {line}"
                firstline = False

            content.append(DECO_SPACE + line)

        content.append(DECO_SEP)

content = "".join(content)

with CHANGE_LOG_TEX_FILE.open(
    mode     = 'w',
    encoding = 'utf-8'
) as f:
    f.write(f"{text_start}{content}{text_end}")


# ------------------------------------ #
# -- UPDATING THE CHANGE LATEX CODE -- #
# ------------------------------------ #

with MAIN_DOC_LOG_TEX_FILE.open(
    mode     = "r",
    encoding = "utf-8"
) as f:
    content = f.read()


before, after = content.split("\\date{")
_, after      = after.split("}", maxsplit = 1)

content = before + "\\date{" + lastdate + "}" + after


before, after = content.split("Version \\texttt{")
_, after      = after.split("}", maxsplit = 1)

content = before + "Version \\texttt{" + lastversion + "}" + after




with MAIN_DOC_LOG_TEX_FILE.open(
    mode     = 'w',
    encoding = 'utf-8'
) as f:
    f.write(content)
