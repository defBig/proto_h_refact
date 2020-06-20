#!/usr/bin/env python3

""" ***********************************************************************                                                                 *
 *   Copyright (C) 2020 Pedro Victor de Brito Cordeiro                    *
 *                      <pedrocga1.opensource@gmail.com>                  *
 *                                                                        *
 *   This script is free software: you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published    *
 *   by the Free Software Foundation, either version 3 of the License,    *
 *   or (at your option) any later version.                               *
 *                                                                        *
 *   This script is distributed in the hope that it will be useful,       *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty          *
 *   of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.              *
 *                                                                        *
 *   See the GNU General Public License at http://www.gnu.org/licenses/   *
 *   for more details.                                                    *
 ********************************************************************** """

import re
import sys
from os import listdir, path
from typing import List

def isPrototype(line: str) -> bool:
    # if a line in proto.h starts if any of these, that line is not a prototype:
    filter = ["typedef", "functionptrtype"]
    if re.match(r'\w+ \*?\w+\(.+', line) and line.split()[0] not in filter:
        return True

def upToParentesis(line: str) -> str:
    return re.findall(r"\w+ \*?\w+\(", line)[0]

def linesUpTo(regex: str, lines: List[str]) -> int:
    total: int = 0
    for line in lines:
        if re.match(regex, line):
            break
        total += 1
    return total

def getNewPrototype(proto: List[str], filename: str) -> List[str]:
    newProto: List[str] = []
    srcLines: List[str] = []
    with open(filename, 'r') as f:
        srcLines = [line.rstrip() for line in f.readlines()]
    for i, srcLine in enumerate(srcLines):
        if upToParentesis(proto[0]) in srcLine:
            newProto = srcLines[i : i + linesUpTo('{', srcLines[i:])]
            newProto[-1] += ';'
            break
    return newProto

def main(argv: str):
    protoH: List[str] = open(path.join('src', 'proto.h'), 'r').read() \
                            .split('\n')

    protos: List[List[str]] = []
    for i, line in enumerate(protoH):
        if isPrototype(line):
            # append all lines from this line to the line ending with a ';'
            # this covers all prototypes, including those spanning multiple
            # lines
            protos.append( protoH[ i : i + linesUpTo('.*;$', protoH[i:]) + 1] )

    # assuming this script is placed at the root of the filetree...
    sourceNames: List[str] = []
    for filename in listdir('src'):
        if filename.endswith('.c'):
            sourceNames.append(path.join('src', filename))

    newProtos: List[List[str]] = []
    for proto in protos:
        succeded = False
        for source in sourceNames:
            # this function takes some time, so I'm gonna store the returned
            # value in a temporary variable
            x = getNewPrototype(proto, source)
            # if it returns a empty list, then it's not in this source
            if x != []:
                newProtos.append(getNewPrototype(proto, source))
                succeded = True
        if not succeded:
            print(f'{proto} has no definition')
            # Gonna keep the prototype for now, and decide wether to remove it
            # or not later
            newProtos.append(proto)

    for proto, newProto in zip(protos, newProtos):
        for i, line in enumerate(protoH):
            if proto[0] == line and proto != newProto:
                protoH = protoH[:i] + newProto + protoH[ i + len(proto) : ]

    outFilename = "proto.h" if len(argv) == 1 else argv[1]
    out = open(outFilename, 'w')
    out.write('\n'.join(protoH))
    out.close()

    print(f"Finished {outFilename}")

if __name__ == "__main__":
    main(sys.argv)
