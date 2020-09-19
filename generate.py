
import math
import os 
import sys 
import fontTools.designspaceLib as designspace
import fontforge

os.makedirs("build/masters_ufo", exist_ok=True)
os.makedirs("/tmp/font-generation/", exist_ok=True)

family_name = "Roland"
slant_angle = 20
separation_width = 125
separation_kerning = 150
kern_touch = 1

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
instances = [
    [["Thin", 100],["Extra Light", 200],["Light", 300],["", 400],["Medium", 500],["Semi Bold", 600],["Bold", 700],["Extra Bold", 800],["Black", 900]],
    [["", 100],["Condensed", 75],["Expanded", 125],],
]
special_instances = []

options = set(sys.argv)

def baseWidth(glyph):
    return glyph.width - glyph.left_side_bearing - glyph.right_side_bearing

def generateWidths(font, spacing_mult):
    global slant_angle
    global separation_width 
    global separation_kerning
    global kern_touch
    font.encoding = "UnicodeBmp"
    # Create auto width
    font["space"].width = int(400 * spacing_mult)
    font["uni00A0"].width = int(400 * spacing_mult)
    font.selection.select("\"", "'", " ", "uni00A0") # Select characters that I don't want to change
    font.selection.invert()
    font.autoWidth(int(separation_width * spacing_mult), minBearing=int(5 * spacing_mult), maxBearing=int(separation_width * spacing_mult / 2), loopCnt=10000)
    # Create auto kerning
    font.addLookup("Kerning", "gpos_pair", None, (("kern",(("DFLT",("dflt")), ("latn",("dflt")),)),))
    font.addLookupSubtable("Kerning", "Kerning-1")
    font.selection.select(
        "cent", "sterling", "currency", "Euro", "mu",
        ("ranges", None), "A", "Z",
        ("ranges", None), "a", "z",
        ("ranges", None), "zero", "nine",
        ("ranges", None), "Agrave", "Odieresis",
        ("ranges", None), "Oslash", "odieresis",
        ("ranges", None), "oslash", "ydieresis",
    ) # Only kern alphanumeric characters
    font.autoKern("Kerning-1", int(separation_kerning * spacing_mult), touch=kern_touch, onlyCloser=True)
    # Generate auto hint
    font.selection.all()
    font.autoHint()
    font.autoInstr()

def setFontDesc(font, weight):
    global family_name
    font.familyname = family_name
    font.fullname = family_name + " Variable"
    font.fontname = family_name + "Variable"
    font.weight = "Variable"
    font.encoding = "UnicodeBmp"
    font.ascent = 800
    font.descent = 200
    font.os2_xheight = 500
    font.os2_capheight = 750
    font.os2_weight = weight

def getAxisValue(pos, name, default):
    global axises
    for i in range(0, len(axises)):
        if axises[i][1] == name:
            return pos[i]
    return default

def toPos(dict):
    global axises
    pos = []
    for i in range(0, len(axises)):
        if axises[i][1] in dict:
            pos.append(dict[axises[i][1]])
        else:
            pos.append(axises[i][4])
    return pos

# Generate minimum masters
for master in designed_masters:
    font = fontforge.open("masters/" + master[0] + ".sfd")
    setFontDesc(font, getAxisValue(master[1], "weight", 0))
    font.selection.all()
    font.unlinkReferences()
    generateWidths(font, getAxisValue(master[1], "width", 100) / 100)
    # Generate font
    font.generate("build/masters_ufo/" + master[0] + ".ufo")
    all_masters.append(master + [ font ])

# Generate regular masters
if "regular" in options or "all" in options:
    axises[0][4] = 400
    light_fonts = [all_masters[0], all_masters[1], all_masters[2]]
    bold_fonts = [all_masters[3], all_masters[4], all_masters[5]]
    for w in range(0, 3):
        font = fontforge.font()
        setFontDesc(font, 400)
        for glyph in light_fonts[w][2].glyphs():
            font.createInterpolatedGlyph(glyph, bold_fonts[w][2][glyph.glyphname], 0.4)
        generateWidths(font, getAxisValue(light_fonts[w][1], "width", 100) / 100)
        # Generate font
        font.generate("build/masters_ufo/" + light_fonts[w][0].replace("Light", "Regular") + ".ufo")
        all_masters.append([light_fonts[w][0].replace("Light", "Regular") , [400, light_fonts[w][1][1] * 0.4 + bold_fonts[w][1][1] * 0.6], font])

# Generate the real bold condensed
if "condensed" in options or "all" in options:
    # Bold
    bold = all_masters[3][2]
    bold_condensed = all_masters[4][2]
    font = fontforge.font()
    setFontDesc(font, 1000)
    for glyph in bold.glyphs():
        font.createInterpolatedGlyph(glyph, bold_condensed[glyph.glyphname], 2)
    generateWidths(font, 0.5)
    # Generate font
    font.generate("build/masters_ufo/Bold-ExtraCondensed.ufo")
    all_masters.append(["Bold-ExtraCondensed", [1000, 50], font])
    # Regular
    if "regular" in options or "all" in options:
        regular = all_masters[6][2]
        regular_condensed = all_masters[7][2]
        font = fontforge.font()
        setFontDesc(font, 400)
        for glyph in regular.glyphs():
            font.createInterpolatedGlyph(glyph, regular_condensed[glyph.glyphname], 50 / 35)
        generateWidths(font, 0.5)
        # Generate font
        font.generate("build/masters_ufo/Regular-ExtraCondensed.ufo")
        all_masters.append(["Regular-ExtraCondensed", [400, 50], font])

# Generate min and max Spacing fonts
if "spacing" in options or "all" in options:
    axises.append(["spcg", "spacing", 0, 1000, 100])
    instances.append([["", 100],])
    for master in all_masters.copy():
        for sp in range(0, 2):
            font = fontforge.font()
            setFontDesc(font, getAxisValue(master[1], "weight", 0))
            # Find the parameters
            for glyph in master[2].glyphs():
                font.createInterpolatedGlyph(glyph, glyph, 0)
            generateWidths(font, sp * 10 *  getAxisValue(master[1], "width", 100) / 100)
            # Generate font
            font.generate("build/masters_ufo/" + master[0] + ("-MinSpacing" if sp == 0 else "-MaxSpacing") + ".ufo")
            all_masters.append([master[0] + ("-MinSpacing" if sp == 0 else "-MaxSpacing"), master[1] + [ sp * 1000 ], font])
        master[1].append(100)

# Generate mono fonts
if "monospace" in options or "all" in options:    
    axises.append(["mono", "monospace", 0, 1, 0])
    instances.append([["", 0],])
    for master in all_masters.copy():
        font = fontforge.font()
        setFontDesc(font, getAxisValue(master[1], "weight", 0))
        # Find the parameters
        target_width = 500 * getAxisValue(master[1], "width", 100) / 100 + (separation_width * (getAxisValue(master[1], "spacing", 100) - 100) / 100)
        origin_fonts = []
        if getAxisValue(master[1], "weight", 0) == 0:
            origin_fonts = [all_masters[0][2], all_masters[1][2], all_masters[2][2]]
        elif getAxisValue(master[1], "weight", 0) == 1000:
            origin_fonts = [all_masters[3][2], all_masters[4][2], all_masters[5][2]]
        else:
            origin_fonts = [all_masters[6][2], all_masters[7][2], all_masters[8][2]]
        for glyph in origin_fonts[0].glyphs():
            separation_mono = (glyph.left_side_bearing + glyph.right_side_bearing)
            separation_mono *= getAxisValue(master[1], "width", 100) / 100
            if getAxisValue(master[1], "spacing", 100) < 100:
                separation_mono *= getAxisValue(master[1], "spacing", 100) / 100
            else:
                separation_mono += (separation_width * (getAxisValue(master[1], "spacing", 100) - 100) / 100)
            target_base_width = target_width - separation_mono
            interpolate_with = None
            new_glyph = None
            if baseWidth(glyph) > target_base_width:
                interpolate_with = origin_fonts[1][glyph.glyphname]
            else:
                interpolate_with = origin_fonts[2][glyph.glyphname]
            if abs(baseWidth(interpolate_with) - baseWidth(glyph)) > 1:
                q = (target_base_width - baseWidth(glyph)) / (baseWidth(interpolate_with) - baseWidth(glyph))
                if baseWidth(glyph) < target_base_width and q > 1.1:
                    q = 1.1
                new_glyph = font.createInterpolatedGlyph(glyph, interpolate_with, q)
            else:
                new_glyph = font.createInterpolatedGlyph(glyph, interpolate_with, 0)
            if target_base_width < baseWidth(new_glyph) and baseWidth(new_glyph) != 0:
                new_glyph.transform([target_base_width / baseWidth(new_glyph), 0, 0, 1, 0, 0])
                new_glyph.left_side_bearing = int(separation_mono / 2)
                new_glyph.right_side_bearing = int(separation_mono / 2)
            elif target_width != new_glyph.width:
                bearing = new_glyph.left_side_bearing + new_glyph.right_side_bearing
                q = new_glyph.left_side_bearing / bearing
                side_bearing = target_width - baseWidth(new_glyph) - separation_mono
                new_glyph.left_side_bearing = int(separation_mono * q + side_bearing / 2)
                new_glyph.right_side_bearing = int(separation_mono * (1 - q) + side_bearing / 2)
            new_glyph.width = int(target_width)
        # We need a kerning lookup, to interpolate with
        font.addLookup("Kerning", "gpos_pair", None, (("kern",(("DFLT",("dflt")), ("latn",("dflt")),)),))
        font.addLookupSubtable("Kerning", "Kerning-1")
        font["e"].addPosSub("Kerning-1", "X", 0)
        # Generate auto hint
        font.selection.all()
        font.autoHint()
        font.autoInstr()
        # Generate font
        font.generate("build/masters_ufo/Mono-" + master[0] + ".ufo")
        all_masters.append(["Mono-" + master[0], master[1] + [ 1 ], font])
        master[1].append(0)

# Generate slanted fonts
if "slant" in options or "all" in options:
    axises.append(["slnt", "slant", -slant_angle, slant_angle, 0, [(-slant_angle, 0), (0, slant_angle), (slant_angle, 2*slant_angle)]])
    instances.append([["", 20],["Italic", 10],])
    for master in all_masters.copy():
        font = master[2]
        # Make the font italic
        font.italicangle = -20
        font.selection.all()
        font.transform([1, 0, math.tan(math.radians(20)), 1, 0, 0])
        # Generate auto hint
        font.selection.all()
        font.autoHint()
        font.autoInstr()
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
        font.autoInstr()
        # Generate font
        font.generate("build/masters_ufo/" + master[0] + "-Slanted" + ".ufo")
        all_masters.append([master[0] + "-Slanted", master[1] + [ 2*slant_angle ], font])
        master[1].append(slant_angle)

if "monospace" in options or "all" in options:
    special_instances.append(["Mono", toPos({"weight": 400, "monospace": 1, "slant": 20})])

os.system("rm -rf /tmp/font-generation")

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

if "instances" in options:
    # Generate all instances
    os.system("fontmake --verbose WARNING -m build/roland.designspace -o ttf -i --production-names --output-dir build/instances_ttf")

# Generate the variable font
os.system("fontmake --verbose WARNING -m build/roland.designspace -o variable --production-names --output-path build/Roland-Variable.ttf")
