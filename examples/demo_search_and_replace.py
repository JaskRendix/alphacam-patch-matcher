from patchmatcher.geometry import Rectangle
from patchmatcher.matching import replace_geometry
from patchmatcher.tables import load_patch_table

patches = load_patch_table("config/patchSizesTop.txt")

geo = Rectangle(width=3.1, height=4.9, cx=10, cy=20)

new_rect, hole = replace_geometry(geo, patches)

print("Original:", geo)
print("Matched patch:", new_rect)
print("Center hole:", hole)
