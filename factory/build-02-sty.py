#! /usr/bin/env python3

from json import load

from mistool.os_use import PPath
from mistool.string_use import between
from mistool.term_use import ALL_FRAMES, withframe


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR = PPath(__file__).parent

PROJECT_NAME  = "tnsseq"
STY_PATH      = THIS_DIR.parent / f"{PROJECT_NAME}" / f"{PROJECT_NAME}.sty"
JSON_DEP_PATH = THIS_DIR / "x-dep-x.json"

DECO = " "*4

MYFRAME = lambda x: withframe(
    text  = x,
    frame = ALL_FRAMES['latex_pretty']
)


# ----------- #
# -- TOOLS -- #
# ----------- #

def path2title(onepath):
    onepath = relative_path.stem.replace('-', ' ').upper()

    while onepath[0] in " 0123456789":
        onepath = onepath[1:]

    return onepath


def cleansource(text):
    if text.strip():
        text = text.split("\n")

        for i in [0, -1]:
            while not text[i].strip():
                text.pop(i)

    else:
        text = []

    return "\n".join(text)


# ----------------- #
# -- THE IMPORTS -- #
# ----------------- #

with JSON_DEP_PATH.open(
    mode     = "r",
    encoding = "utf-8"
) as jsonfile:
    ALL_IMPORTS_N_TIKZ_LIBS = load(jsonfile)


ALL_IMPORTS = []
lastfirst = ""

for pack, opts in ALL_IMPORTS_N_TIKZ_LIBS["packages"].items():
    newfirst = pack[0]

    if newfirst != lastfirst:
        ALL_IMPORTS.append(f"% {newfirst.upper()}")
        lastfirst = newfirst

    ALL_IMPORTS.append("\\RequirePackage{" + pack + "}")

    if opts:
        for oneoption in opts:
            ALL_IMPORTS.append(
                "\\PassOptionsToPackage{" + oneoption + "}{" + pack + "}"
            )

if ALL_IMPORTS_N_TIKZ_LIBS["tikzlibs"]:
    ALL_IMPORTS.append('')
    ALL_IMPORTS.append('% TikZ libraries')

    for onelib in ALL_IMPORTS_N_TIKZ_LIBS["tikzlibs"]:
        ALL_IMPORTS.append("\\usetikzlibrary{" + onelib + "}")

ALL_IMPORTS = "\n".join(ALL_IMPORTS)

# Trick for bm

ALL_IMPORTS = ALL_IMPORTS.replace(
    r"\RequirePackage{bm}",
    r"""
\newcommand\hmmax{0} % See this post :
\newcommand\bmmax{0} % https://tex.stackexchange.com/a/243541/6880
\RequirePackage{bm}
    """.strip()
)

# ---------------- #
# -- THE MACROS -- #
# ---------------- #

ALL_MACROS         = []
ALL_LOCAL_SETTINGS = []


paths_found = []

for subdir in THIS_DIR.walk("dir::"):
    subdir_name = str(subdir.name)

    if subdir_name in [
        "config",
    ] or subdir_name.startswith("x-"):
        continue

    for latexfile in subdir.walk("file::*.sty"):
        paths_found.append(latexfile)


paths_found.sort()

for latexfile in paths_found:
    relative_path = latexfile - THIS_DIR
    parentname    = latexfile.parent.name

    print(f"{DECO}* Extracting macros from << {relative_path} >>")

    with open(
        file     = latexfile,
        encoding = "utf-8"
    ) as filetoupdate:
        _, packages, definitions = between(
            text = filetoupdate.read(),
            seps = [
                "% == PACKAGES USED == %",
                "% == DEFINITIONS == %"
            ],
            keepseps = False
        )

    definitions = cleansource(definitions)

    if definitions.strip():
        if ALL_MACROS:
            ALL_MACROS.append("\n")

        ALL_MACROS += [
            MYFRAME(path2title(relative_path.stem)),
            "",
            definitions
        ]


ALL_MACROS = "\n".join(ALL_MACROS)


# ------------------------------ #
# -- UPDATE THE MAIN STY FILE -- #
# ------------------------------ #

source = f"""{MYFRAME("IMPORTS REQUIRED")}

{ALL_IMPORTS}


{ALL_MACROS}
"""

STY_PATH.create("file")

with STY_PATH.open(
    mode     = "w",
    encoding = "utf-8"
) as lyxam:
    lyxam.write(source)

print(f"{DECO}* Update of << {STY_PATH.name} >> done.")
