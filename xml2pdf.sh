#!/bin/bash

# Convert XML structure to GraphViz file and render to PDF
# Based on: https://github.com/TomConlin/xpath2dot

AWK_OPTS="-v ORIENT=LR"
DOT_OPTS="-Nfontname=Roboto"

OLD_PWD=$(pwd)

for INFILE in $@; do

    WORKDIR=$(dirname $INFILE)
    FNAME=$(basename $INFILE .xml)

    cd ${WORKDIR} || continue
    xmlstarlet el -a ${FNAME}.xml | sort -u | ${OLD_PWD}/xpath2dot.awk ${AWK_OPTS} > ${FNAME}.dot || continue
    dot -T pdf ${DOT_OPTS} ${FNAME}.dot > ${FNAME}.pdf || continue

    echo "Done: ${FNAME}.xml => ${FNAME}.dot | ${FNAME}.pdf"

done

cd ${OLD_PWD}
