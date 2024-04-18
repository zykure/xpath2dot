#!/usr/bin/env python

#  xpath2dot.py
#
# basic usage:
#   xmlstarlet el file.xml | xpath2dot.py > file.dot
#
# include XML attributes:
#   xmlstarlet el -a file.xml | xpath2dot.py > file.dot
#
# include XML attributes and their values (to detect name references):
#   xmlstarlet el -v file.xml | xpath2dot.py > file.dot
#
# usage with JSON input:
#   json2xml.py file.json | xmlstarlet el - | xpath2dot.py > file.dot
#
# use `dot` or similar commdand to create graphical output:
#   xmlstarlet el file.xml | xpath2dot.py | dot -Tpdf > file.pdf

# xpaths describe how to address an element in an xml document
# xmlstarlet can emit all the xpaths from an xml document
# this script transforms a list of xpaths into a GraphViz dot file
# to capture the relations between elements expressed in the xpaths.
#
# note: Any other method you use to generate xpaths should work as well

# C symbols are limited to upper+lower+digits+underscore
# should be < 32 long and not begin with a digit
# but we are not enforcing inital char or length here
# just replacing runs of non-alphanums with underscore
# so they can be used as node labels in dot
# quoting allows spaces in names but causes other problems
def sanitize(s):
    return s.replace(r' !"#$%&\'()*+,-./:;<=>?@[\\]^`{|}~/', "__")

PENMIN = 2
PENMAX = 5  # max penwidth
RANKDIR = "LR"
FONTNAME = "Roboto"
COLORSCHEME = "rainbow"  # matplotlib colorscheme to color child nodes
NAMEREGEX = r'^([\D]{3,}[\w]*)$'  # attribute must match this regex to be considered as name reference

import sys, re, fileinput, operator

if COLORSCHEME:
    try:
        import matplotlib
        cmap = matplotlib.colormaps.get_cmap(COLORSCHEME)

        def getcolor(n, nmax=50, opacity=0.4):
            rgba = list(cmap(float(n) / nmax))
            rgba[-1] = opacity
            return '#' + ''.join(['%02x' % int(255*c) for c in rgba])

    except ImportError:
        def getcolor(n, nmax=50):
            return "white"

node = {}  # list of nodes; stores attributes as sub-dict
edge = {}  # list of edges; stores reference counts
attv = {}  # list of attr values; stores referencing nodes

# process list of XPaths from input
for line in fileinput.input():
    line = line.strip()

    attrs = {}
    if '[' in line:
        # get attributes as key-value dict from XPath
        # format: `.../element[@attr1='value1' and @attr2='value2' and ...]`
        assert(line.endswith(']'))
        line, alist = line[:-1].split('[', maxsplit=1)

        for elem in alist.split(' and '):
            key, value = elem.split('=', maxsplit=1)
            assert(key.startswith('@'))
            key = key[1:]
            assert(value[0] == "'" and value[-1] == "'")
            value = value[1:-1]
            attrs[key] = value

    elif '@' in line:
        # get attributes as key-value dict from XPath
        # format: `.../element/@attr1`
        line, key = line.split('/@', maxsplit=1)
        attrs[key] = ""

    # get XPath as array
    xpath = line.split('/')
    if len(xpath) <= 1:
        continue

    # define the node
    leaf = '__'.join(map(sanitize, xpath[:-1]))
    if leaf not in node:
        node[leaf] = {}
        node[leaf]['_name_'] = sanitize(xpath[-2])
        node[leaf]['_rank_'] = len(xpath) - 1
        node[leaf]['_childcolor_'] = getcolor(len(node))
        node[leaf]['_color_'] = "white"

    # define the 1st edge for this node
    nextleaf = '__'.join(map(sanitize, xpath))
    if nextleaf not in node:
        node[nextleaf] = {}
        node[nextleaf]['_name_'] = sanitize(xpath[-1])
        node[nextleaf]['_rank_'] = len(xpath)
        node[nextleaf]['_childcolor_'] = getcolor(len(node))
        node[nextleaf]['_color_'] = node[leaf]['_childcolor_']

    if (leaf, nextleaf) not in edge:
        edge[(leaf, nextleaf)] = 0
    edge[(leaf, nextleaf)] += 1

    # track node attribute usage and named references
    for key, value in attrs.items():
        att = sanitize(key)
        if att not in node[nextleaf]:
            node[nextleaf][att] = 0
        node[nextleaf][att] += 1

        if value:
            if not value in attv:
                attv[value] = set()
            attv[value].add(nextleaf)

edge2 = {}

# process list of named references
for val,ref in attv.items():
    if not re.match(NAMEREGEX, val):
        continue

    ref = list(ref)
    if len(ref) <= 1:  # ignore unique references
        continue

    # generate pair-wise edges over the list of referencing nodes
    for i in range(len(ref)):
        if i == 0:  # closes the loop
            leaf = ref[0]
            nextleaf = ref[-1]
        else:
            leaf = ref[i-1]
            nextleaf = ref[i]

        if leaf == nextleaf:  # ignore self-references
            continue

        # define the 2nd edge for this node
        if (leaf, nextleaf) not in edge2:
            edge2[(leaf, nextleaf)] = 0
        edge2[(leaf, nextleaf)] += 1

# find edge (node pair) with greatest count for scaling if need be
if edge:
    norm = max(edge.items(), key=operator.itemgetter(1))[1]
    if norm < 1.0:
        norm = 1.0
    if PENMAX and (norm > PENMAX):
        norm = norm / PENMAX

if edge2:
    norm2 = max(edge2.items(), key=operator.itemgetter(1))[1]
    if norm2 < 1.0:
        norm2 = 1.0
    if PENMAX and (norm2 > PENMAX):
        norm2 = norm2 / PENMAX

def gtable(rows, border=0, cellborder=1, cellspacing=1, cellpadding=4, bgcolor="none"):
    return f"<<TABLE border=\"{border}\" cellborder=\"{cellborder}\" cellspacing=\"{cellspacing}\" cellpadding=\"{cellpadding}\" bgcolor=\"{bgcolor}\">{rows}</TABLE>>"

def gcell(text):
    return f"<TR><TD>{text}</TD></TR>"

def ghead(text):
    return gcell("<B>" + text + "</B>")

print("digraph G{")
print(f"overlap = false; charset = \"utf-8\";")
print(f"rankdir = {RANKDIR};")
print(f"graph [fontname = \"{FONTNAME}\"];")
print(f"node  [fontname = \"{FONTNAME}\"];")
print(f"edge [fontname = \"{FONTNAME}\"];")

print()
for n in node:
    name = node[n]["_name_"]
    rank = node[n]["_rank_"]
    color = node[n]["_color_"]
    attributes = ""
    for a in node[n]:
        if not a.startswith("_"):
            attributes = attributes + gcell(a)
    print(f"    {n} [label = {gtable(ghead(name) + attributes, bgcolor=color)} shape = none];")

# note well:
# edge weight relates to _reuse_ of element name pairs within the xml schema
# and not reuse of a particular element
print()
for e in edge:
    print(f"    {e[0]} -> {e[1]} [penwidth = \"{PENMIN+(edge[e]/norm-1):.3f}\", weight = \"{edge[e]:.3f}\"];")

print()
for e in edge2:
    print(f"    {e[0]} -> {e[1]} [penwidth = \"{PENMIN+(edge2[e]/norm2-1):.3f}\", weight = \"{edge2[e]:.3f}\", style = dashed, dir = both];")

print()
print("subgraph cluster_01{")
if edge:
    print(f"    A1 [label = {gtable(ghead('A'))} shape = none];")
    print(f"    B1 [label = {gtable(ghead('B'))} shape = none];")
    print(f"    A1 -> B1 [label = \"Child Element\", penwidth = \"{PENMIN}\", weight = \"1\"];")
if edge2:
    print(f"    A2 [label = {gtable(ghead('A'))} shape = none];")
    print(f"    B2 [label = {gtable(ghead('B'))} shape = none];")
    print(f"    A2 -> B2 [label = \"Name Reference\", penwidth = \"{PENMIN}\", weight = \"1\", style = dashed, dir = both];")
print("}")

print()
print("}")

sys.exit(0)
