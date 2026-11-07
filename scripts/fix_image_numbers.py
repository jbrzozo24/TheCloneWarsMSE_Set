# helper to format nandeck


path = r"C:\Users\jbrzo\Desktop\workroot\magic_the_gathering\MagicSetEditor_Sets\TheCloneWars\nandeck\Nandeckmythic.txt"

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

with open(path, "w", encoding="utf-8") as f:
    for i, line in enumerate(lines, start=1):
        f.write(line.replace("IMAGE=1,", f"IMAGE={i},", 1))
