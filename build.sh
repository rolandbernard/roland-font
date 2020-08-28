
fontforge -script ./masters/generate.pe ./masters/Light.sfd ./masters/Light.ufo
fontforge -script ./masters/generate.pe ./masters/Bold.sfd ./masters/Bold.ufo

fontmake -m Roland.designspace -o variable --production-names --output-path Roland.ttf
