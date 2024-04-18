#!/bin/bash

rm -f *.png

for fname in *.xml; do

    echo ${fname}

    xmlstarlet el -u ${fname} | ../xpath2dot.py | dot -Tpng > ${fname}.png
    xmlstarlet el -a ${fname} | ../xpath2dot.py | dot -Tpng > ${fname}+attr.png
    xmlstarlet el -v ${fname} | ../xpath2dot.py | dot -Tpng > ${fname}+name.png

    ../xml2json.py ${fname} > $(echo ${fname} | sed -r 's/\.xml/\.json/')

done

for fname in *.json; do

    echo ${fname}

    ../json2xml.py ${fname} | xmlstarlet el -u | ../xpath2dot.py | dot -Tpng > ${fname}.png

done
