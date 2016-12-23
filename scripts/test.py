#!/Users/fireharp/Documents/Prog/HS_AI/venv/bin/python
import xmltodict

for i in xrange(1000):
    with open('./data/sample/replays/urkUd6LDtvQkBBMzEQ2f6V.hsreplay.xml') as fd:
        doc = xmltodict.parse(fd.read())
