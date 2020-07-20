from pathlib import Path


# ----------------------- #
# -- TOOLS & CONSTANTS -- #
# ----------------------- #

PROJECT_DIR  = Path(__file__).parent.parent
ABOUT_README = PROJECT_DIR / 'about' / 'readme' / 'main.md'
README       = PROJECT_DIR / 'README.md'


# ------------------------ #
# -- UPDATE THE CONTENT -- #
# ------------------------ #

about_content = []
add_content   = False

tab = " "*4

with ABOUT_README.open(
    encoding = 'utf-8',
    mode     = "r"
) as aboutfile:
    for line in aboutfile:
        line = line.rstrip()

        if line == "content::":
            add_content = True

        elif add_content:
            if line.startswith(tab):
                line = line.lstrip()

                subcontent_file = ABOUT_README.parent

                for piece in line.split("/"):
                    subcontent_file /= piece

                if not subcontent_file.is_file():
                    raise ValueError(
                        "unexisting subcontent << {0} >>".format(line)
                    )

                with subcontent_file.open(encoding = 'utf-8', mode = "r") as sf:
                    subcontent = sf.read()

                if about_content and about_content[-1] != "":
                    about_content.append("")
                    about_content.append("")

                about_content.append(subcontent.strip())

            else:
                add_content = False
                about_content.append(line)

        else:
            about_content.append(line)

about_content = "\n".join(about_content)


# --------------------- #
# -- UPDATE THE FILE -- #
# --------------------- #

with README.open(
    encoding = 'utf-8',
    mode     = "w"
) as readmefile:
    readmefile.write(about_content)
