#!/usr/bin/env python3

import xmltodict, json, sys

fname = sys.argv[1] if len(sys.argv) > 1 else None
with open(fname) if fname else sys.stdin as f:
    o = json.loads(f.read())
    print(xmltodict.unparse(o, pretty=True))
