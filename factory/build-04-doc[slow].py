#! /usr/bin/env python3

from mistool.latex_use import Build, clean as latexclean
from mistool.os_use import PPath
from mistool.string_use import between, MultiReplace
from orpyste.data import ReadBlock


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR = PPath( __file__ ).parent

PROJECT_NAME  = "tnsseq"
TEMPLATE_PATH = THIS_DIR / "config" / "doc[fr].tex"
DIR_DOC_PATH  = THIS_DIR.parent / f"{PROJECT_NAME}"
DOC_PATH      = DIR_DOC_PATH / f"{PROJECT_NAME}-doc[fr].tex"

DOUBLE_BRACES = MultiReplace({
    '{': '{'*2,
    '}': '}'*2
})

PYFORMAT = MultiReplace({
    '%((': '{',
    '))%': '}'
})


LATEX_SECTIONS = [
    section
    for section in """
\\section
\\subsection
\\subsubsection
\\paragraph
\\textit
    """.strip().split("\n")
]

LATEX_LOWER_SECTIONS = {
    section: LATEX_SECTIONS[len(LATEX_SECTIONS) - i]
    for i, section in enumerate(LATEX_SECTIONS[::-1][1:], 1)
}

LATEX_SECTIONS.pop(-1)

NB_SECTIONS     = len(LATEX_SECTIONS)
LAST_HUMAN_SECS = [("", "")]*NB_SECTIONS


DECO = " "*4


# ----------- #
# -- TOOLS -- #
# ----------- #

def startingtech(text):
    text = text.strip()

    if text.startswith("%"):
        return False

    return "{Fiches techniques}" in text \
        or "{Fiche technique}" in text


def levelsmaller(level_1, level_2):
    return LATEX_SECTIONS.index(level_1) >= LATEX_SECTIONS.index(level_2)


def extract_level(line):
    for level in LATEX_SECTIONS:
        if line.startswith(level):
            return level

    return ""


def close_techsec(line, level):
    thislevel = extract_level(line.strip())

    return (thislevel and level and levelsmaller(level, thislevel))


def extract_title(level, lines, i):
    infos = lines[i]

# We have to take care of the following case.
#
# \subsection{\texorpdfstring{Les opérateurs $\pp{}$ et $\dd{}$}%
#                            {Les opérateurs "d rond" et "d droit"}}
    if "\\texorpdfstring" in infos:
        i     += 1
        infos += "\n" + lines[i]

    title = infos[len(level):]

    return i, title


def downgrade_levels(techcontent):
    for old, new in LATEX_LOWER_SECTIONS.items():
        techcontent = techcontent.replace(old, new)

    return techcontent


def update_humansecs(seclevel, title):
    global LAST_HUMAN_SECS

    pos = LATEX_SECTIONS.index(seclevel)

    LAST_HUMAN_SECS = LAST_HUMAN_SECS[:pos+1] \
                    + [("", "")]*(NB_SECTIONS - 1 - pos)

    LAST_HUMAN_SECS[pos] = (seclevel, title)


def extracttechtitle(level, latexfile):
    global LAST_HUMAN_SECS

    goodpos = - 1

    for pos, (prevlevel, prevtitle) in enumerate(LAST_HUMAN_SECS):
        if level == prevlevel:
            goodpos = pos
            break

    if goodpos == -1:
        raise Exception(
            "Illegal use of a title for a technical section. See :"
            f"    * {latexfile}"
        )

    content_tiles = []

    for i in range(goodpos+1):
        if LAST_HUMAN_SECS[i][0]:
            latex, title = LAST_HUMAN_SECS[i]

            content_tiles += [
                f"{latex}{title}",
                ""
            ]

            LAST_HUMAN_SECS[i] = ('', '')

    content_tiles = "\n".join(content_tiles)

    return content_tiles


# ------------ #
# -- HEADER -- #
# ------------ #

with open(
    file     = THIS_DIR / "config" / "header[fr].sty",
    encoding = "utf-8"
) as headerfile:
    HEADER = headerfile.read().strip()


# ---------------------- #
# -- LOOKING FOR DOCS -- #
# ---------------------- #

LATEXFILES = []

for subdir in THIS_DIR.walk("dir::"):
    subdir_name = str(subdir.name)
    subdir_str  = str(subdir)

    if subdir_name in ["config", "style"] \
    or "x-" in subdir_str:
        continue

    LATEXFILES += [
        lat
        for lat in subdir.walk("file::*\[fr\].tex")
        if not lat.stem.endswith("-nodoc[fr]")
    ]


LATEXFILES.sort()


TECHNIC_CONTENTS = []
HUMAN_CONTENTS   = []

for latexfile in LATEXFILES:
# Content
    with latexfile.open(
        mode     = "r",
        encoding = "utf-8"
    ) as texfile:
        _, content, _ = between(
            text = texfile.read(),
            seps = [
                r"\begin{document}",
                r"\end{document}"
            ]
        )

    content = content.strip()

# Lines
#
# We need i in case of use of \texorpdfstring.
    lines = content.split("\n")
    i     = 0

# Our "local" variables.
    humancontent = []

    techcontent   = []
    addtotech     = False
    lasttechlevel = ""

    for i, aline in enumerate(lines):
# New section for technical infos
        if startingtech(aline):
            addtotech     = True
            lasttechlevel = extract_level(aline)
            techcontent  += [extracttechtitle(lasttechlevel, latexfile), ""]

            continue

# A line to add.
#
# Dow have to close a technical section ?
        if addtotech and close_techsec(aline, lasttechlevel):
            addtotech = False

# A technical line.
        if addtotech:
            techcontent.append(aline)

# A human line.
        else:
            seclevel = extract_level(aline)

            if seclevel:
# i can change because of the use of \texorpdfstring.
                iold = i

                i, title = extract_title(
                    seclevel,
                    lines,
                    i
                )

                if i != iold:
                    aline += lines[i]

                update_humansecs(seclevel, title)

            humancontent.append(aline)

# Lower level for sections.
    techcontent = "\n".join(techcontent)
    techcontent = techcontent.strip()

    if techcontent:
        techcontent = downgrade_levels(techcontent)

# Clean the human content.
    humancontent = "\n".join(humancontent)
    humancontent = humancontent.strip()

# Store the contents.
    TECHNIC_CONTENTS += ["", "", techcontent]
    HUMAN_CONTENTS.append(humancontent)


# ------------------------- #
# -- UPDATE THE DOC FILE -- #
# ------------------------- #

with TEMPLATE_PATH.open(
    mode     = "r",
    encoding = "utf-8"
) as docfile:
    content = DOUBLE_BRACES(docfile.read())
    content = PYFORMAT(content)
    content = content.format(
        header    = HEADER,
        content   = "\n".join(HUMAN_CONTENTS),
        technical = "\n".join(TECHNIC_CONTENTS),
    )


with DOC_PATH.open(
    mode     = "w",
    encoding = "utf-8"
) as docfile:
    docfile.write(content)


print(f"{DECO}* Update of << {DOC_PATH.name} >> done.")


# ------------------------------- #
# -- COMPILE ALL THE DOCS FILE -- #
# ------------------------------- #
nbrepeat = 3

for latexpath in DIR_DOC_PATH.walk(f"file::*.tex"):
    print(
        f"{DECO}* Compilations of << {latexpath.name} >> started : {nbrepeat} times."
    )

    builder = Build(
        ppath      = latexpath,
        repeat     = nbrepeat,
        showoutput = True
    )
    builder.pdf()

    print(
        f"{DECO}* Compilation of << {latexpath.name} >> finished.",
        f"{DECO}* Cleaning extra files.",
        sep = "\n"
    )

latexclean(DIR_DOC_PATH)
