#! /usr/bin/env python3

from collections import defaultdict
from json import dumps
import re

from mistool.latex_use import about
from mistool.os_use import PPath
from mistool.string_use import between
from mistool.term_use import ALL_FRAMES, withframe


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR = PPath(__file__).parent

JSON_DEP_PATH = THIS_DIR / "x-dep-x.json"


DECO = " "*4

MYFRAME = lambda x: withframe(
    text  = x,
    frame = ALL_FRAMES['latex_pretty']
)

PATTERN_CMD_NAME = re.compile("^\\\([a-zA-Z]+)")
PATTERN_OPTIONS  = re.compile("^\\[(.+?)\\]")
PATTERN_IN_CURLY = re.compile("^\\{(.+?)\\}(.*)$")

ABOUT_LATEX = about()

PACKAGE_ID, TIKZLIB_ID, KIND_ID, NAMES_ID, OPTIONS_ID = range(5)


# ----------- #
# -- TOOLS -- #
# ----------- #

def path2title(onepath):
    onepath = relative_path.stem.replace('-', ' ').upper()

    while onepath[0] in " 0123456789":
        onepath = onepath[1:]

    return onepath


def analyze(info, nobug = False):
    m = PATTERN_CMD_NAME.match(info)

# RequirePackage, usepackage, ...
    if m is None:
        if nobug:
            return None

        raise Exception("Illegal initial value:", info)

    kind = m.group(1)
    info = info[len(kind)+1:].strip()

    if kind in ['RequirePackage', 'usepackage']:
        kind = PACKAGE_ID

    elif kind == 'usetikzlibrary':
        kind = TIKZLIB_ID

    else:
        if nobug:
            return None

        raise Exception("Illegal kind:", info)

# Removed the latex comments.
    i = info.find('%')

    if i != -1:
        info = info[:i].strip()

# Option given inside brackets ?
    m = PATTERN_OPTIONS.match(info)

    if m is None:
        options = []

    else:
        options = [
            o.strip()
            for o in m.group(1).split(',')
        ]

        info = info[len(m.group(1))+2:].strip()

# No curly braces
#
# WARNING ! Extra infos ignored m.group(2).
    m = PATTERN_IN_CURLY.match(info)

    names = m.group(1)
    names = [
        n.strip()
        for n in names.split(',')
    ]

# All the job has been done.
    meta = {
        KIND_ID : kind,
        NAMES_ID: names,
    }

    if kind == PACKAGE_ID:
        meta[OPTIONS_ID] = options

    return meta


def minify(packages):
    locallatexdir = PPath("/usr/local/texlive/2020/texmf-dist")

    stdimports = defaultdict(list)

    print(
        f"{DECO}* Trying to analyze imports of the offical sty files"
    )

    for stdsty in locallatexdir.walk("file::**.sty"):
        stdname = stdsty.stem

        if stdname in packages:
            print(
                f"{DECO*2}- Looking inside the offical << {stdsty.name} >>"
            )

            with stdsty.open(
                mode     = "r",
                encoding = "utf-8"
            ) as stdfile:
                for oneline in stdfile.readlines():
                    oneline = oneline.strip()

                    if not oneline:
                        continue

                    info = analyze(info = oneline, nobug = True)

                    if info is None:
                        continue

                    if info[KIND_ID] == PACKAGE_ID:
                        stdimports[stdname] += info[NAMES_ID]

                if stdname not in stdimports:
                    stdimports[stdname] = []

# Local sty.
    localpackages = set(packages) - set(stdimports.keys())

# Let's minimize.
    somecleaningdone = True

    while(somecleaningdone):
        somecleaningdone = False

        for pack in stdimports:
            for _, itsimports in stdimports.items():
                if pack in itsimports:
                    somecleaningdone = True
                    break

            if somecleaningdone:
                del stdimports[pack]
                break

    shortlist = list(stdimports) + list(localpackages)

    return sorted(shortlist)


def builddep(styfiles):
    allinfos = {
        PACKAGE_ID: defaultdict(set),
        TIKZLIB_ID: set(),
    }

    for onestyfile in styfiles:
        relative_path = onestyfile - THIS_DIR
        parentname    = onestyfile.parent.name

        print(f"{DECO}* Analyzing << {relative_path} >>")

        with open(
            file     = onestyfile,
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

        for info in packages.split("\n"):
            info = info.strip()

            if not info:
                continue

            info = analyze(info)

            if info[KIND_ID] == TIKZLIB_ID:
                for onename in info[NAMES_ID]:
                    allinfos[TIKZLIB_ID].add(onename)

            elif info[KIND_ID] == PACKAGE_ID:
                for onename in info[NAMES_ID]:
                    if onename not in allinfos[PACKAGE_ID]:
                        allinfos[PACKAGE_ID][onename] = set(info[OPTIONS_ID])

    return allinfos


# ---------------- #
# -- LET'S WORK -- #
# ---------------- #

paths_found = []

for subdir in THIS_DIR.walk("dir::"):
    subdir_name = str(subdir.name)

    if subdir_name in [
        "config",
    ] or subdir_name.startswith("x-"):
        continue

    for onestyfile in subdir.walk("file::*.sty"):
        paths_found.append(onestyfile)

paths_found.sort()

packages        = builddep(paths_found)
needed_packages = minify(packages[PACKAGE_ID])

packages["packages"] = {
    pack: list(packages[PACKAGE_ID][pack])
    for pack in sorted(packages[PACKAGE_ID])
    if pack in needed_packages
}
del packages[PACKAGE_ID]

packages["tikzlibs"] = list(packages[TIKZLIB_ID])
del packages[TIKZLIB_ID]


with JSON_DEP_PATH.open(
    mode     = "w",
    encoding = "utf-8"
) as jsonfile:
    jsonfile.write(dumps(packages))
