
fontforge -script ./masters/generate.pe ./masters/Light.sfd ./masters/Light.ufo
fontforge -script ./masters/generate.pe ./masters/Bold.sfd ./masters/Bold.ufo
fontforge -script ./masters/generate.pe ./masters/Light-Condensed.sfd ./masters/Light-Condensed.ufo

fontmake -m Roland.designspace -o variable --production-names --output-path Roland.ttf
