
### XPath to GraphViz dot


Started as a [question on Stack Overflow](https://stackoverflow.com/questions/36327815/converting-random-xml-file-to-tree-diagram/36349048#36349048)
a couple of years ago but now gets used often enough to keep around.

### Requirements:
 -  A way to generate [xpaths](https://en.wikipedia.org/wiki/XPath)
 from an XML file,  I use [xmlstarlet](https://en.wikipedia.org/wiki/XMLStarlet)
 -  This xpath2dot [awk](https://en.wikipedia.org/wiki/AWK) script.
 -  A way to directly view (xdot), or convert to image a [Graphviz dot file](https://en.wikipedia.org/wiki/Graphviz)

### Simple Usage:

Starting with a XML file which might change or go away from
`ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/xml/sample_xml/RCV000077146.xml`

```
wget -q ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/xml/sample_xml/RCV000077146.xml
```

Which I will keep a snapshot of [here](https://raw.githubusercontent.com/zykure/xpath2dot/master/examples/RCV000077146.xml).


```
xmlstarlet el -u RCV000077146.xml | xpath2dot.py | dot -T png > xpath2dot_demo.png
xmlstarlet el -v RCV000077146.xml | xpath2dot.py | dot -T png > xpath2dot_demo.png
```

### Result:

![Example xpath2dot output](https://raw.githubusercontent.com/zykure/xpath2dot/master/examples/RCV000077146.xml.png)


### More Usage:

Include XML attributes:

```
xmlstarlet el -a RCV000077146.xml | sort -u | xpath2dot.awk | dot -T png > xpath2dot_demo.png
```
### Result:

![Example xpath2dot with attributes output](https://raw.githubusercontent.com/zykure/xpath2dot/master/examples/RCV000077146.xml+attr.png)


### Even More Usage:

Include XML name references:

```
xmlstarlet el -v RCV000077146.xml | xpath2dot.awk | dot -T png > xpath2dot_demo.png
```
### Result:

![Example xpath2dot with references output](https://raw.githubusercontent.com/zykure/xpath2dot/master/examples/RCV000077146.xml+name.png)
