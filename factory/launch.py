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

SUFFIX_CFG = {
    "extra": ('-nox', '--noextra'),
    "slow" : ('-nos', '--noslow'),
}

EXT_2_CMDS = {
    "py": 'python',
    "sh": 'bash'
}

PPATH_PATTERNS = [
    f"file::build-*.{ext}"
    for ext in EXT_2_CMDS
]


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


for suffix, (sname, lname) in SUFFIX_CFG.items():
    parser.add_argument(
        sname, lname,
        action  = "store_true",
        default = False,
        help    = "ask to only execute the scripts without the suffix "
                 f" ``[{suffix}]`` "
                  "(some builders are only useful few times)."
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

option2suffix = {
    lname[2:]: f"[{suffix}]"
    for suffix, (_, lname) in SUFFIX_CFG.items()
}

allpaths = [
    p
    for pattern in PPATH_PATTERNS
    for p in THIS_DIR.walk(pattern)
]

allpaths.sort()


for onepath in allpaths:
    filename = (onepath - THIS_DIR).stem

    nolaunch = False

    for option, suffix in option2suffix.items():
        if getattr(ARGS, option) \
        and filename.endswith(suffix):
            print(f"- No suffix {suffix} : << {filename} >> ignored.")

            nolaunch = True

    if nolaunch:
        continue

    print(f'+ Launching "{filename}"')

    cmd = EXT_2_CMDS[onepath.ext]

    runthis(
        cmd        = f'{cmd} "{onepath}"',
        showoutput = True
    )
