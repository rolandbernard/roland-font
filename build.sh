
fontforge -script ./masters/generate.pe ./masters/Light-Regular.sfd ./masters/Light-Regular.ufo &> /dev/null
fontforge -script ./masters/generate.pe ./masters/Bold-Regular.sfd ./masters/Bold-Regular.ufo &> /dev/null

fontmake -m Roland.designspace -o variable --production-names --output-path Roland.ttf
