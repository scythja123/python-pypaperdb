import lxml.etree as ET
import paperdb.databaseBase
from paperdb.entry import Entry
from io import StringIO
from collections import Counter
from paperdb.warning import *
import logging
log =logging.getLogger(__name__)

# SAVEMODE NEWCONVERT only used for converting the old style db to the new one
SAVEMODE = "NEWCONVERT"  # OLD, NEW or NEWCONVERT

if __name__ == "__main__":
    # Someone launches this class directly
    print("please run application to start Paperdatabase")

class Database(paperdb.databaseBase.Database):

    charmap = {'\n': '<br>'}
    replaceChars = lambda self, myStr: str.join('',[self.charmap.get(c,c) for c in str(myStr)])
    charNewline = {'\n': ' '}
    removeNewline = lambda self, myStr: str.join('',[self.charNewline.get(c,c) for c in str(myStr)])

   
    def __init__(self,dbFile):
        paperdb.databaseBase.Database.__init__(self,dbFile)

        self.parser = ET.XMLParser(remove_blank_text = True)
        try:
            self.tree = ET.parse(self.dbFile,self.parser)
            print("Opened " + dbFile)
        except IOError:
            print("File " + dbFile +" not found, creating new database")
            
            # The basic sceleton
            # xmlstr = """
            # <bibliography>
            # <entries>

            # </entries>
            # </bibliography>
            # """
            xmlstr = """
                  <bibliography>
                  <indexing>
                  <entryTypes>
                  <entryType>
                  <id> 0 </id>
                  <key> Paper </key>
                  </entryType>
                  <entryType>
                  <id> 1 </id>
                  <key> Book </key>
                  </entryType>
                  <entryType>
                  <id> 2 </id>
                  <key> Thesis </key>
                  </entryType>
                  <entryType>
                  <id> 3 </id>
                  <key> Presentation </key>
                  </entryType>
                  <entryType>
                  <id> 4 </id>
                  <key> Course - Notes </key>
                  </entryType>
                  </entryTypes>
                  </indexing>
                  <entries>
                  </entries>
                  </bibliography>
            """

       
            self.tree = ET.parse(StringIO(xmlstr.format()),self.parser)
            self.docinfo = self.tree.docinfo

            self._writeXML()

        self.__parseXML()

    def __parseXML(self):
        self.tree = ET.parse(self.dbFile,self.parser)
        self.docinfo = self.tree.docinfo
        self.root = self.tree.getroot()
        self.entryRoot = self.root.find('entries')
        if self.entryRoot is None:
            self.root.insert(0, ET.Element('entries'))
            self.entryRoot = self.root.find('entries')
        self.indexRoot = self.root.find('indexing')
        if self.indexRoot is None:
            self.root.insert(0, ET.Element('indexing'))
            self.indexRoot = self.root.find('indexing')
                             
        self._findKeywords()
    

    def searchEntry(self,searchid):
        dbentry = self.__searchid(searchid)
        return(self.__returnEntry(dbentry) if dbentry is not None else None)

    def existsid(self,searchid):
        return (self.__searchid(searchid) is not None)
    
    def __searchid(self,searchid):
        self.__parseXML()

        for dbentry in self.entryRoot.findall('entry'):
            entryid = dbentry.find('id').text
            
            if entryid == searchid:
                return dbentry
            
        return None

    def getAllTopics(self):
        
        if self.indexRoot is None:  # If we can't find indexRoot, we don't have to search for topics
            return None
        
        topicList = self.indexRoot.find('topics')
        
        if topicList is None or len(topicList) == 0:
            log.debug("no topics found")
            return None
        
        topics = [None] * (int(topicList[-1].find('id').text) + 1) # preallocate array for topics
       
        for dbentry in topicList:
            topics[int(dbentry.find('id').text)] = dbentry.find('key').text

        log.debug("topics: " + ", ".join(topics))
        return topics

    def getAllEntryTypes(self):

        if self.indexRoot is None:  # If we can't find indexRoot, we don't have to search for entryTypes
            return None
                
        entryTypeList = self.indexRoot.find('entryTypes')

        if entryTypeList is None or len(entryTypeList) == 0:
            log.debug("no entry types found")
            return None
        
        entryTypes = [None] * (int(entryTypeList[-1].find('id').text) + 1) # preallocate array for topics
       
        for dbentry in entryTypeList:
            entryTypes[int(dbentry.find('id').text)] = dbentry.find('key').text

        log.debug("entryTypes: " + ", ".join(entryTypes))
            
        return entryTypes

    
    def getAllEntries(self):
        entries=[]
        for dbentry in self.entryRoot.findall('entry'):
            entries.append(self.__returnEntry(dbentry))
        return entries

    def getFirstEntries(self,number):
        entries=[]
        for dbentry in self.entryRoot.findall('entry')[:number]:
            entries.append(self.__returnEntry(dbentry))
        return entries

    def getEntries(self,keywords):
        #print(keywords)
        entries=set([])
        for dbentry in self.entryRoot.findall('entry'):
            for line in keywords:

                try:
                    topic = dbentry.findtext('topic')
                    entryTopic = int(topic) if topic is not None else 0
                except:
                    entryTopic = 0
                
                if (line[3]==None or line[3]== entryTopic):
                    if (line[2]==None or line[2]==int(dbentry.findtext('paperType'))):
                        if line[1] == 'any':
                            foundText = ''
                            for child in dbentry:
                                if child.text is not None:
                                    foundText = foundText + child.text.lower() + ','
                        elif line[1] == 'keyword':
                            foundText =''
                            for kwd in dbentry.iter('stichwort'):
                                foundText = foundText + kwd.text.lower() +','
                        else:
                            foundText = dbentry.findtext(line[1]).lower()

                        andKeywords = [x.strip() for x in line[0].split(',')]
                        usableEntry = True
                        for keyword in andKeywords:
                            if keyword.startswith("~"):
                                keywordb = str.replace(keyword,"~","")
                                if keywordb.lower() in foundText:
                                    usableEntry = False
                            else:        
                                if keyword.lower() not in foundText:
                                    usableEntry = False
                        if usableEntry:
                            entries.add(self.__returnEntry(dbentry))
        return entries
    
            
    def __returnEntry(self,searchid):

        # set bibtex fields, if it exists otherwise set the fields seperately
        if searchid.findtext('bibTex') is not None and searchid.findtext('bibTex') is not "" and searchid.findtext('bibTex').strip("\n").strip().lower() is not "todo":
            entry = Entry(searchid.findtext('bibTex'),self.__bibparser,self.__bibwriter)

        else: # this is for thbackwards compatibility needed
            entry = Entry("@misc{doe2013,\n author = {Wombat, the Happy},\n title = {An amazing title}\n}",self.__bibparser,self.__bibwriter)

            entry.entryId = searchid.findtext('id').strip()
            entry.title = searchid.findtext('title').strip()

            year = searchid.findtext('year').strip()
            entry.year = year if year is not None else ""

            author = searchid.findtext('author').strip()
            entry.author = author if author is not None else ""

            journal = searchid.findtext('journal').strip()
            entry.journal = journal if journal is not None else ""

            entry.link2pdf = searchid.findtext('linkToPdf') if searchid.findtext('linkToPdf') is not None else ""

        # set the fields unrelated to the bibtex
        entry.pdfFile = searchid.findtext('pdfFilePath').strip()
        entry.abstract = searchid.findtext('abstract') if searchid.findtext('abstract') is not None else ""
        entry.summary = searchid.findtext('summary') if searchid.findtext('summary') is not None else ""

        entry.date = searchid.findtext('updated') if searchid.findtext('updated') is not None else ""

        printed = searchid.findtext('inPaperform')
        entry.printed = int(printed) if printed else 0

        paperType = searchid.findtext('paperType')
        entry.paperType = int(paperType) if paperType is not None else 0

        citing  = searchid.findtext('citing')
        entry.citing = citing if citing is not None else ""
        favorite = searchid.findtext('favorite')
        entry.favorite = int(favorite) if favorite is not None else 0

        kwds = searchid.findall('stichwort')
        entry.keywords = [kwd.text for kwd in kwds]

        topic = searchid.findtext('topic')
        try:
            entry.topic = int(topic) if topic is not None else 0
        except:
            entry.topic = 0
        
        entry.iddb = entry.entryId 
        return entry

       
    def store(self,dbentry,tag,value):
        xmlentry = dbentry.find(tag)
        if xmlentry is None:
            xmlentry = ET.SubElement(dbentry,tag)


        if SAVEMODE is "OLD":
            xmlentry.text = value 
        elif SAVEMODE is "NEW" or SAVEMODE is "NEWCONVERT":
            xmlentry.text = self.replaceChars(value)  # Escape newline chars

    def save(self,entry):

        self.__parseXML()        
        dbentry = self.__searchid(entry.iddb)

        if dbentry is None:
            dbentry = ET.SubElement(self.entryRoot,'entry')
            entryid = ET.SubElement(dbentry,'id')
        else:
            entryid  = dbentry.find('id')
        
        entryid.text = entry.entryId
        self.store(dbentry,'title',self.removeNewline(entry.title))
        self.store(dbentry,'inPaperform',entry.printed)
        self.store(dbentry,'pdfFilePath',entry.pdfFile)
        self.store(dbentry,'abstract',entry.abstract)
        self.store(dbentry,'summary',entry.summary)
        self.store(dbentry,'linkToPdf',entry.link2pdf)
        self.store(dbentry,'bibTex',entry.bibtex)
        self.store(dbentry,'paperType',entry.paperType)
        self.store(dbentry,'citing',entry.citing)
        self.store(dbentry,'author',entry.author)
        self.store(dbentry,'year',entry.year)
        self.store(dbentry,'journal',entry.journal)
        self.store(dbentry,'favorite',entry.favorite)
        self.store(dbentry,'updated',entry.date)
        self.store(dbentry,'topic',entry.topic)
            
        for kwd in dbentry.findall('stichwort'): # delete all keyword fields
            dbentry.remove(kwd)
        
        # add keywords    
        for kwd in entry.keywords:
            if len(kwd) is not 0:
                newkwd = ET.SubElement(dbentry,'stichwort')
                if SAVEMODE is "OLD":
                    newkwd.text = kwd
                elif SAVEMODE is "NEW" or SAVEMODE is "NEWCONVERT":
                    newkwd.text = self.replaceChars(kwd) # Escape newline chars


        if SAVEMODE is "OLD":
            self._writeXML() # store file
        elif SAVEMODE is "NEWCONVERT" or SAVEMODE is "NEW":
            self._writeXMLLineWise() # store file line-wise
            
        entry.iddb = entry.entryId # Store the changed ID


    def _writeXML(self):
        self.tree.write(self.dbFile,pretty_print = True, xml_declaration = True)
        print("write database")
        
    def _writeXMLLineWise(self):
        xmlStr = """<?xml version='1.0' encoding='UTF-8'?>\n <!DOCTYPE bibliography SYSTEM 'hest'>\n\n<bibliography>\n"""

        # Start printing the indexing terms. No need to use a linespace for this


        xmlStr += ET.tostring(self.indexRoot,method='xml',with_tail=True,encoding='unicode',pretty_print=True)
        
        # Make the child that contains the entries (TODO: Maybe we can pretty print the entire thing at once now when HG is set to XML mode.)
        xmlStr += '<entries>\n'
        
        for entry in self.entryRoot:            
            if SAVEMODE is "NEWCONVERT":
                xmlStr += '\n' + self.removeNewline(ET.tostring(entry,method='xml',encoding='unicode',with_tail=True)) + '\n'
               
            elif SAVEMODE is "NEW":
                xmlStr += '\n' + ET.tostring(entry,method='xml',with_tail=True,encoding='unicode') + '\n'

        xmlStr += "</entries>\n</bibliography>\n"
                
        Fhandle = open(self.dbFile,"w",encoding='utf8')
        if Fhandle is None:
            error("Database-file %s could not be opened" %self.dbFile)
        else:
            Fhandle.write(xmlStr)
            Fhandle.close()
        log.info("saved database")

    def remove(self,entryid):
        self.__parseXML()

        dbentry = self.__searchid(entryid)
        
        if dbentry is not None:
            self.entryRoot.remove(dbentry)

    def _findKeywords(self):
        kwdList = []
        for entry in self.entryRoot:
            kwds = [kwd.text for kwd in entry.findall('stichwort')]
            kwdList.extend(kwds)
            
        cnt = Counter(kwdList).most_common()
        self._kwdlist = [kwd[0] for kwd in cnt]
