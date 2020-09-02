
import os 
import fontTools.designspaceLib as designspace
import fontforge

os.makedirs("build/masters_ufo", exist_ok=True)

family_name = "Roland"
axises = [
    ["wgth", "weight", 0, 1000, 0],
    ["wdth", "width", 50, 150, 100],
    ["slnt", "slant", 0, 20, 0],
]
designed_masters = [
    ["Light", [ 0, 100 ]], 
    ["Light-Condensed", [ 0, 50 ]], 
    ["Light-Expanded", [ 0, 150 ]], 
    ["Bold", [ 1000, 100 ]], 
    ["Bold-Condensed", [ 1000, 75 ]], 
    ["Bold-Expanded", [ 1000, 150 ]]
]
all_masters = []
instances = [
    [
        ["", 400],
        ["Bold", 700],
        ["Light", 200]
    ],
    [
        ["", 100],
        ["Condensed", 75],
        ["Expanded", 125]
    ],
    [
        ["", 0],
        ["Italic", 10],
    ]
]

# Generate UFOs
for master in designed_masters:
    font = fontforge.open("masters/" + master[0] + ".sfd")
    font.familyname = family_name
    font.fullname = family_name + " Variable"
    font.weight = "Variable"
    # Create auto width
    font.selection.select("\"") # Select characters that I don't want to change
    font.selection.invert()
    font.autoWidth(100, minBearing=20)
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
    font.autoKern("Kerning-1", 100)
    font.generate("build/masters_ufo/" + master[0] + ".ufo")
    all_masters.append(master + [ font ])
# Generate slanted fonts
for master in all_masters.copy():
    font = master[2]
    # Make the font italic
    font.italicangle = -20
    font.selection.all()
    font.italicize(italic_angle = -20)
    font.generate("build/masters_ufo/" + master[0] + "-Italic" + ".ufo")
    all_masters.append([master[0] + "-Italic", master[1] + [ 20 ], font])
    master[1].append(0)

document = designspace.DesignSpaceDocument()
for axis in axises:
    a = designspace.AxisDescriptor()
    a.tag = axis[0]
    a.name = axis[1]
    a.minimum = axis[2]
    a.maximum = axis[3]
    a.default = axis[4]
    document.addAxis(a)

for master in all_masters:
    s = designspace.SourceDescriptor()
    s.path = "build/masters_ufo/" + master[0] + ".ufo"
    s.familyName = family_name
    s.styleName = master[0].replace("-", " ")
    s.location = dict()
    for i in range(0, len(axises)):
        s.location[axises[i][1]] = master[1][i]
    if master == all_masters[0]:
        s.copyLib = True
        s.copyInfo = True
        s.copyGroups = True
        s.copyFeatures = True
    document.addSource(s)

instances_resolved = []
for ax in instances:
    if len(instances_resolved) != 0:
        old_instances_resolved = instances_resolved
        instances_resolved = []
        for value in ax:
            for el in old_instances_resolved:
                instances_resolved.append([el[0].strip() + " " + value[0], el[1] + [value[1]]])
    else:
        for value in ax:
            instances_resolved.append([value[0], [value[1]]])
for instance in instances_resolved:
    instance[0] = instance[0].strip()
    if len(instance[0]) == 0:
        instance[0] = "Regular"

for instance in instances_resolved:
    i = designspace.InstanceDescriptor()
    i.familyName = family_name
    i.styleName = instance[0]
    i.path = "build/instances_ufo/" + instance[0].replace(" ", "-") + ".ufo"
    i.location = dict()
    for j in range(0, len(axises)):
        i.location[axises[j][1]] = instance[1][j]
    i.kerning = True
    i.info = True
    document.addInstance(i)

document.write("build/roland.designspace")

# Generate all instances as ttf
os.system("fontmake --verbose WARNING -m build/roland.designspace -o ufo ttf -i --production-names --output-dir build/instances_ttf")
# Generate the variable font
os.system("fontmake --verbose WARNING -m build/roland.designspace -o variable --production-names --output-path build/Roland.ttf")
