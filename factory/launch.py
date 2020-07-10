#!/usr/bin/env python3

import argparse

from mistool.os_use import (
    cd,
    PPath,
    runthis
)


from mistool.string_use import joinand


# --------------- #
# -- CONSTANTS -- #
# --------------- #

THIS_DIR  = PPath(__file__).parent

EXT_2_CMDS = {
    "py"  : 'python',
    "bash": 'bash'
}

PPATH_PATTERNS = [
    f"file::build-*.{ext}"
    for ext in EXT_2_CMDS
]

SLOW_SUFFIX = "[slow]"


# --------- #
# -- CLI -- #
# --------- #

DESC  = "This file looks for scripts named ``build-*`` with extensions "
DESC += joinand([
    f"``.{ext}`` [{cmd}]"
    for ext, cmd in EXT_2_CMDS.items()
])
DESC += ". The scripts founded are executed using natural sorting on their paths."

parser = argparse.ArgumentParser(
    description = DESC,
)


parser.add_argument(
    '-nos', '--noslow',
    action  = "store_true",
    default = False,
    help    = "ask to only execute the scripts without the suffix "
             f" ``{SLOW_SUFFIX}`` "
              "(some long builders are only useful few times)."
)

parser.add_argument(
    '-nor', '--norec',
    action  = "store_true",
    default = False,
    help    = "ask to only execute the scripts inside the same folder "
              "of the actual script ``launch.py``."
)

ARGS = parser.parse_args()

if not ARGS.norec:
    PPATH_PATTERNS += [
        f"file::**build-*.{ext}"
        for ext in EXT_2_CMDS
    ]


# -------------------------------------- #
# -- LAUNCHING ALL THE BUILDING TOOLS -- #
# -------------------------------------- #

allpaths = [
    p
    for pattern in PPATH_PATTERNS
    for p in THIS_DIR.walk(pattern)
]

allpaths.sort()


for onepath in allpaths:
    filename = (onepath - THIS_DIR).stem

    if ARGS.noslow and filename.endswith(SLOW_SUFFIX):
        print(f'- Ignoring  "{filename}" <-- no slow option activated')
        continue

    print(f'+ Launching "{filename}"')

    cmd = EXT_2_CMDS[onepath.ext]

    runthis(
        cmd        = f'{cmd} "{onepath}"',
        showoutput = True
    )
