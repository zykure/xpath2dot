#! /usr/bin/awk -f

#  xpath2dot.awk
#
# usage:
#   xmlstarlet el -a file.xml | sort -u | xpath2dot.awk > file.dot
#   xmlstarlet el -a file.xml | sort -u | xpath2dot.awk -v ORIENT="UD" > file.dot

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
function sanitize(var){
    gsub(/[ !"#$%&'()*+,\-./:;<=>?@[\\\]\^`{|}~]+/, "__", var);
    return var
}



BEGIN{
    # graphs can be oriented verticaly  up/down (UD)
    # or horizontaly left/right (LR)  which is the default here
    # to change default on command line include
    # -v ORIENT="UD"
    if(! ORIENT)
        ORIENT="LR"
    FS="/";  # XPath delimiter
    penmax=10  # max penwidth
}

# xpaths with at least two elements will be either:
#	an edge between nodes
#	or an attribute within a node
# it is only the last two elements in each xpath we are capturing

NF > 1 {
    # use full path (up to NF-1) to identify a node
    leaf = ""
    for(i=1; i<NF; i++){
        leaf = leaf "__" sanitize($i)
    }
    # store the node name for later
    node[leaf]["_name_"] = sanitize($(NF-1))
    if(1 == match($NF, "@")){
        att = sanitize(substr($NF,2));
        node[leaf][att]++  # gathering but not using attribute usage counts
    } else {
        # storing edges in an assocative array means parallel edges collapse
        nextleaf = leaf "__" sanitize($(NF))
        node[nextleaf]["_name_"] = sanitize($(NF))
        edge[leaf " -> " nextleaf]++;
    }
}

END{
    # find edge (node pair) with greatest count for scaling if need be
    # may need more tweaking
    x = asort(edge,ma)
    norm = ma[x]
    if(norm < 1.0) norm = 1.0
    if(penmax && (norm > penmax)) norm = norm / penmax

    print "digraph G{"
    print "overlap=false;"
    print "rankdir=" ORIENT "; charset=\"utf-8\";"
    # the node array now contains ALL nodes, but only some have attributes other than "_name_"
    for(n in node){
        name = node[n]["_name_"]
        attributes = ""
        for(a in node[n]){
            if(a != "_name_"){
                attributes = attributes "<TR><TD>" a "</TD></TR>"
            }
        }
        print n " [label = <<TABLE border=\"0\" cellborder=\"1\" cellspacing=\"0\" cellpadding=\"4\"><TR><TD><B>" name "</B></TD></TR>" attributes "</TABLE>> shape = \"none\"];"
    }
    # note well
    # edge weight relates to _reuse_ of element name pairs within the xml schema
    # and not reuse of a particular element
    for(e in edge){
        print e " [penwidth = \""(edge[e]/norm) "\", weight = \"" edge[e] "\"];"
    }
    print "}"
}
