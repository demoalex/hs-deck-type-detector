#!/usr/bin/python
import xmltodict

with open('./data/sample/replays/urkUd6LDtvQkBBMzEQ2f6V.hsreplay.xml') as fd:
    doc = xmltodict.parse(fd.read())

