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


def closetechsec(line, level):
    thislevel = extractlevel(line.strip())

    return (
        thislevel
        and
        LATEX_SECTIONS.index(level) >= LATEX_SECTIONS.index(thislevel)
    )


def extractlevel(line):
    for level in LATEX_SECTIONS:
        if line.startswith(level):
            return level

    return ""


def extracttitle(level, lines, i):
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


def extracttechtitle(level, line):
    global LAST_HUMAN_SEC

    i = len(LAST_HUMAN_SEC) - 1

    while(LAST_HUMAN_SEC[i][0] != level):
        i -= 1

    return LAST_HUMAN_SEC[i][0] + LAST_HUMAN_SEC[i][1]


def updatelevels(techcontent):
    for old, new in LATEX_LOWER_SECTIONS.items():
        techcontent = techcontent.replace(old, new)

    return techcontent


# ------------------------- #
# -- COPYING EXTRA FILES -- #
# ------------------------- #

for img in THIS_DIR.walk("file::**\[fr\].png"):
    if img.stem.endswith("-nodoc[fr]"):
        continue

    img.copy_to(
        DIR_DOC_PATH / img.name,
        safemode = False
    )


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

HUMAN_CONTENTS   = []
TECHNIC_CONTENTS = []
LATEXFILES       = []

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

LAST_HUMAN_SEC = []
LAST_SECTION   = ""


for latexfile in LATEXFILES:
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
    lines   = content.split("\n")
# We need i in case of use of \texorpdfstring.
    i       = 0

    humancontent = []

    techcontent   = []
    addtotech     = False
    lasttechlevel = ""

    for i, aline in enumerate(lines):
# New section for technical infos
        if startingtech(aline):
            addtotech = True

            if LAST_SECTION:
                techcontent += [LAST_SECTION, ""]
                LAST_SECTION  = ""

            lasttechlevel = extractlevel(aline)

            if lasttechlevel != "\\section":
                techcontent += [
                    extracttechtitle(lasttechlevel, aline),
                    ""
                ]

            LAST_HUMAN_SEC = []

            continue

# A line to add.
#
# Dow have to close a technical section ?
        if addtotech and closetechsec(aline, lasttechlevel):
            addtotech = False

# A technical line.
        if addtotech:
            techcontent.append(aline)

# A human line.
        else:
            seclevel = extractlevel(aline)

            if seclevel:
# i can change because of the use of \texorpdfstring.
                iold = i

                i, title = extracttitle(
                    seclevel,
                    lines,
                    i
                )

                if i != iold:
                    aline += lines[i]

                LAST_HUMAN_SEC.append((seclevel, title))

                if seclevel == "\\section":
                    LAST_SECTION = aline

            humancontent.append(aline)

# Lower level for sections.
    techcontent = "\n".join(techcontent)
    techcontent = techcontent.strip()

    if techcontent:
        techcontent = updatelevels(techcontent)

# Clean the human content.
    humancontent = "\n".join(humancontent)
    humancontent = humancontent.strip()

# Store the contents.
    TECHNIC_CONTENTS.append(techcontent)
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
