# This script generates only one variable font that contains only the weight and width axises

import math
import os 
import fontTools.designspaceLib as designspace
import fontforge

os.makedirs("build/masters_ufo", exist_ok=True)

family_name = "Roland"
axises = [
    ["wght", "weight", 0, 1000, 0],
    ["wdth", "width", 50, 150, 100],
]
designed_masters = [
    ["Light", [ 0, 100 ]], 
    ["Light-Condensed", [ 0, 50 ]], 
    ["Light-Expanded", [ 0, 150 ]], 
    ["Bold", [ 1000, 100 ]], 
    ["Bold-Condensed", [ 1000, 75 ]], 
    ["Bold-Expanded", [ 1000, 150 ]],
]
all_masters = []
separation_width = 75
separation_kerning = 125
kern_touch = 1

# Generate UFOs
for master in designed_masters:
    font = fontforge.open("masters/" + master[0] + ".sfd")
    font.familyname = family_name
    font.fullname = family_name + " Variable"
    font.weight = "Variable"
    # Create auto width
    font["space"].width = int(400 * master[1][1] / 100)
    font.selection.select("\"", " ", "'") # Select characters that I don't want to change
    font.selection.invert()
    font.autoWidth(int(separation_width * master[1][1] / 100))
    # Create auto kerning
    font.addLookup("Kerning", "gpos_pair", None, (("kern",(("DFLT",("dflt")), ("latn",("dflt")),)),))
    font.addLookupSubtable("Kerning", "Kerning-1")
    font.selection.select(
        ("ranges", None), "A", "Z",
        ("ranges", None), "a", "z",
        ("ranges", None), "zero", "nine",
        ("ranges", None), "Agrave", "Odieresis",
        ("ranges", None), "Oslash", "odieresis",
        ("ranges", None), "oslash", "ydieresis",
    ) # Only kern alphanumeric characters
    font.autoKern("Kerning-1", int(separation_kerning * master[1][1] / 100), touch=kern_touch, onlyCloser=True)
    # Generate auto hint
    font.selection.all()
    font.autoHint()
    # Generate font
    font.generate("build/masters_ufo/" + master[0] + ".ufo")
    all_masters.append(master + [ font ])

document = designspace.DesignSpaceDocument()
for axis in axises:
    a = designspace.AxisDescriptor()
    a.tag = axis[0]
    a.name = axis[1]
    a.minimum = axis[2]
    a.maximum = axis[3]
    a.default = axis[4]
    if len(axis) > 5:
        a.map = axis[5]
    document.addAxis(a)

for master in all_masters:
    s = designspace.SourceDescriptor()
    s.path = "build/masters_ufo/" + master[0] + ".ufo"
    s.familyName = family_name
    s.styleName = master[0].replace("-", " ")
    s.location = dict()
    for i in range(0, len(axises)):
        s.location[axises[i][1]] = master[1][i]
    document.addSource(s)

document.write("build/roland.designspace")

# Generate the variable font
os.system("fontmake --verbose WARNING -m build/roland.designspace -o variable --production-names --output-path build/Roland_Min.ttf")