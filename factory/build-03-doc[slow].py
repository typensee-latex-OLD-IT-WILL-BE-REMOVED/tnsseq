#! /usr/bin/env python3

from mistool.latex_use import Build, clean as latexclean
from mistool.os_use import PPath
from mistool.string_use import between, MultiReplace
from mistool.term_use import ALL_FRAMES, withframe
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


# ----------- #
# -- TOOLS -- #
# ----------- #

DECO = " "*4

MYFRAME = lambda x: withframe(
    text  = x,
    frame = ALL_FRAMES['latex_pretty']
)


def startingtech(text):
    return "{Fiches techniques}" in text \
        or "{Fiche technique}" in text


LATEX_SECTIONS = [
    section
    for section in """
\\section
\\subsection
\\subsubsection
\\paragraph
    """.strip().split("\n")
]

def closetechsec(text, section):
    if not section:
        raise Exception("Empty section for technical reports !")

    text = text.strip()

    pos = LATEX_SECTIONS.index(section)

    for sublevel in LATEX_SECTIONS[:pos+1]:
        if text.startswith(sublevel):
            return True

    return False


# ---------------------- #
# -- COPYING PICTURES -- #
# ---------------------- #

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

# Extract technical infos
        if not startingtech(content):
            humancontent = content
            techcontent  = ""

        else:
            humancontent = []
            techcontent  = []
            addtotech    = False
            latexsectech = ""

            for i, line in enumerate(content.split("\n")):
                if i == 0:
                    if not line.startswith("%"):
                        techcontent  += [" ", " ", line]

                    humancontent += [" ", " ", line]

                    continue

                if startingtech(line):
                    addtotech       = True
                    latexsectech, _ = line.split("{", maxsplit = 1)
                    continue

                if addtotech \
                and closetechsec(line, latexsectech):
                    addtotech = False

                if addtotech:
                    techcontent.append(line)

                else:
                    humancontent.append(line)


            techcontent = "\n".join(techcontent)
            techcontent = techcontent.strip()

            for i, section in enumerate(LATEX_SECTIONS[::-1][1:], -1):
                techcontent = techcontent.replace(
                    section,
                    LATEX_SECTIONS[i]
                )

            techcontent = techcontent.replace(
                "\\paragraph",
                "\\subsubsection"
            )


            humancontent = "\n".join(humancontent)
            humancontent = humancontent.strip()


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
