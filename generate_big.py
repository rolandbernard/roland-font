
import math
import os 
import fontTools.designspaceLib as designspace
import fontforge

def baseWidth(glyph):
    return glyph.width - glyph.left_side_bearing - glyph.right_side_bearing

os.makedirs("build/masters_ufo", exist_ok=True)

family_name = "Roland"
slant_angle = 20
axises = [
    ["wght", "weight", 0, 1000, 0],
    ["wdth", "width", 50, 150, 100],
    ["spcg", "spacing", 0, 500, 100],
    ["mono", "monospace", 0, 1, 0],
    ["slnt", "slant", -slant_angle, slant_angle, 0, [(-slant_angle, 0), (0, slant_angle), (slant_angle, 2*slant_angle)]],
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
instances = [
    [["Thin", 100],["Extra Light", 200],["Light", 300],["", 400],["Medium", 500],["Semi Bold", 600],["Bold", 700],["Extra Bold", 800],["Black", 900]],
    [["", 100],["Condensed", 75],["Expanded", 125],],
    [["", 100],],
    [["", 0],],
    [["", 20],["Italic", 10],],
]
special_instances = [
    ["Mono", [400, 100, 0, 1, 0]],
]
separation_width = 75
separation_kerning = 100
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

# Generate the real bold condensed
if True:
    bold = all_masters[3][2]
    bold_condensed = all_masters[4][2]
    font = fontforge.font()
    for glyph in bold.glyphs():
        font.createInterpolatedGlyph(glyph, bold_condensed[glyph.glyphname], 2)
    font.familyname = family_name
    font.fullname = family_name + " Variable"
    font.weight = "Variable"
    font.ascent = 800
    font.descent = 200
    font.os2_xheight = 500
    font.os2_capheight = 750
    font.os2_weight = 1000
    # Create auto width
    font["space"].width = 200
    font.selection.select("\"", " ", "'") # Select characters that I don't want to change
    font.selection.invert()
    font.autoWidth(int(separation_width / 2))
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
    font.autoKern("Kerning-1", int(separation_kerning / 2), touch=kern_touch, onlyCloser=True)
    # Generate auto hint
    font.selection.all()
    font.autoHint()
    # Generate font
    font.generate("build/masters_ufo/Bold-ExtraCondensed.ufo")
    all_masters.append(["Bold-ExtraCondensed", [1000, 50], font])

# Generate min and max Spacing fonts
for master in all_masters.copy():
    for sp in range(0, 2):
        font = fontforge.font()
        # Find the parameters
        for glyph in master[2].glyphs():
            font.createInterpolatedGlyph(glyph, glyph, 0)
        font.familyname = family_name
        font.fullname = family_name + " Variable"
        font.weight = "Variable"
        font.ascent = 800
        font.descent = 200
        font.os2_xheight = 500
        font.os2_capheight = 750
        font.os2_weight = master[1][0]
        # Create auto width
        font["space"].width = int(400 * 5 * master[1][1] / 100)
        font.selection.select("\"", " ", "'") # Select characters that I don't want to change
        font.selection.invert()
        font.autoWidth(int(separation_width * sp * 5 * master[1][1] / 100))
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
        font.autoKern("Kerning-1", int(separation_kerning * sp * 5 * master[1][1] / 100), touch=kern_touch, onlyCloser=True)
        # Generate auto hint
        font.selection.all()
        font.autoHint()
        # Generate font
        font.generate("build/masters_ufo/" + master[0] + ("-MinSpacing" if sp == 0 else "-MaxSpacing") + ".ufo")
        all_masters.append([master[0] + ("-MinSpacing" if sp == 0 else "-MaxSpacing"), master[1] + [ sp * 500 ], font])
    master[1].append(100)

# Generate mono fonts
for master in all_masters.copy():
    if True:
        font = fontforge.font()
        # Find the parameters
        target_width = 500 * master[1][1] / 100
        origin_fonts = []
        if master[1][0] == 0:
            origin_fonts = [all_masters[0][2], all_masters[1][2], all_masters[2][2]]
            target_width += 4
        else:
            origin_fonts = [all_masters[3][2], all_masters[4][2], all_masters[5][2]]
            target_width += 40
        for glyph in origin_fonts[0].glyphs():
            interpolate_with = None
            new_glyph = None
            if glyph.width > target_width:
                interpolate_with = origin_fonts[1][glyph.glyphname]
            else:
                interpolate_with = origin_fonts[2][glyph.glyphname]
            if abs(interpolate_with.width - glyph.width) > 1:
                q = (target_width - glyph.width) / (interpolate_with.width - glyph.width)
                if glyph.width < target_width and q > 1.1:
                    q = 1.1
                new_glyph = font.createInterpolatedGlyph(glyph, interpolate_with, q)
            else:
                new_glyph = font.createInterpolatedGlyph(glyph, interpolate_with, 0)
            if target_width > new_glyph.width:
                side_bearing = int((target_width - baseWidth(new_glyph)) / 2)
                new_glyph.left_side_bearing = side_bearing
                new_glyph.right_side_bearing = side_bearing
            elif target_width < new_glyph.width and baseWidth(new_glyph) != 0:
                new_glyph.transform([(target_width - 40) / baseWidth(new_glyph), 0, 0, 1, 0, 0])
                new_glyph.left_side_bearing = 20
                new_glyph.right_side_bearing = 20
            new_glyph.width = int(target_width)
        font.familyname = family_name
        font.fullname = family_name + " Variable"
        font.weight = "Variable"
        font.ascent = 800
        font.descent = 200
        font.os2_xheight = 500
        font.os2_capheight = 750
        font.os2_weight = master[1][0]
        # We need a kerning lookup, to interpolate with
        font.addLookup("Kerning", "gpos_pair", None, (("kern",(("DFLT",("dflt")), ("latn",("dflt")),)),))
        font.addLookupSubtable("Kerning", "Kerning-1")
        font["e"].addPosSub("Kerning-1", "X", 0)
        # Generate auto hint
        font.selection.all()
        font.autoHint()
        # Generate font
        font.generate("build/masters_ufo/Mono-" + master[0] + ".ufo")
        all_masters.append(["Mono-" + master[0], master[1] + [ 1 ], font])
    master[1].append(0)
    
# Generate slanted fonts
for master in all_masters.copy():
    if True:
        font = master[2]
        # Make the font italic
        font.italicangle = -20
        font.selection.all()
        font.transform([1, 0, math.tan(math.radians(20)), 1, 0, 0])
        # Generate auto hint
        font.selection.all()
        font.autoHint()
        # Generate font
        font.generate("build/masters_ufo/" + master[0] + "-Italic" + ".ufo")
        all_masters.append([master[0] + "-Italic", master[1] + [ 0 ], font])
        # Make the font italic
        font.italicangle = 20
        font.selection.all()
        font.transform([1, 0, math.tan(math.radians(-20)), 1, 0, 0])
        font.transform([1, 0, math.tan(math.radians(-20)), 1, 0, 0])
        # Generate auto hint
        font.selection.all()
        font.autoHint()
        # Generate font
        font.generate("build/masters_ufo/" + master[0] + "-Slanted" + ".ufo")
        all_masters.append([master[0] + "-Slanted", master[1] + [ 2*slant_angle ], font])
    master[1].append(slant_angle)

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
            
instances_resolved += special_instances
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
os.system("fontmake --verbose WARNING -m build/roland.designspace -o ttf -i --production-names --output-dir build/instances_ttf")
# Generate the variable font
os.system("fontmake --verbose WARNING -m build/roland.designspace -o variable --production-names --output-path build/Roland_Max.ttf")