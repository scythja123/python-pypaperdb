#!/usr/bin/python2.7
from xmldb import Database
import lxml.etree as ET


def convert(dbFile,convertOutputFile):
    print "Converting %s to %s" %(dbFile, convertOutputFile)
    db = Database(dbFile)
    dbNew = Database(convertOutputFile)
    dbNew.SAVEMODE = "NEWCONVERT"
    for entry in db.root:
        if not isinstance(entry,ET._Comment):
            entryData = db.searchEntry(entry.find('id').text)
            entryData.abstract = db.removeNewline(unicode(entryData.abstract))
            if "sonja" not in entryData.keywords and "edwin" not in entryData.keywords:
                entryData.keywords.append("sonja")
            dbNew.save(entryData)

    db = Database(convertOutputFile)
    db._writeXMLLineWise()

if __name__ == "__main__":

    dbFile = "../database.xml"
    
    convert(dbFile,"../databaseconv.xml") 
