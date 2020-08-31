
mkdir -p ./build/masters_ufo/

fontforge -script ./masters/generate.pe ./masters/Light.sfd ./build/masters_ufo/Light.ufo
fontforge -script ./masters/generate.pe ./masters/Light-Condensed.sfd ./build/masters_ufo/Light-Condensed.ufo
fontforge -script ./masters/generate.pe ./masters/Light-Expanded.sfd ./build/masters_ufo/Light-Expanded.ufo

fontforge -script ./masters/generate.pe ./masters/Bold.sfd ./build/masters_ufo/Bold.ufo
fontforge -script ./masters/generate.pe ./masters/Bold-Condensed.sfd ./build/masters_ufo/Bold-Condensed.ufo
fontforge -script ./masters/generate.pe ./masters/Bold-Expanded.sfd ./build/masters_ufo/Bold-Expanded.ufo

# Generate the Regular instance in order to use it as the default
fontmake -m regular.designspace -o ufo -i --production-names
# Generate all instances as ttf
fontmake -m roland.designspace -o ufo ttf -i --production-names --output-dir ./build/instances_ttf
# Generate the variable font
fontmake -m roland.designspace -o variable --production-names --output-path ./build/Roland.ttf
