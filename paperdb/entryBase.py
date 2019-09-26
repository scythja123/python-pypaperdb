import re ,datetime, socket

# external package
import bibtexparser

import itertools
import logging
log =logging.getLogger(__name__)


charmap2 = {'<br>': '\n'}
#replaceChars = lambda self, myStr: str.join('',[self.charmap.get(c,c) for c in str(myStr)])

# remove this
def replaceChars2(text):
    for key in charmap2:
        text = text.replace(key, charmap2[key])
    return text

      

class Entry:

    # what is that for? remove this?
    charNewline = {'\n': ' '}
    removeNewline = lambda self, myStr: str.join('',[self.charNewline.get(c,c) for c in myStr])
    charmap = {'\"': '&quot;',
               '\'': '&apos;',
               '<':  '&lt;',
               '>':  '&gt;',
               '&':  '&amp;'}
    escape = lambda self, myStr: str.join("",[self.charmap.get(c,c) for c in myStr])

    # to store the variables that are not part of the bibtex entry
    iddb = ""
    abstract = ""
    summary =""
    pdfFile = ""
    keywords = []
    date = ""
    
    # initialise the entry.
    # requires a bibtex string, the parser and writer, 
    def __init__(self, bibtex, bibparser, bibwriter, pdfFile = "", keywords = "", abstract = "", summary = ""):
        try:
            if (bibparser.is_parser() and bibwriter.is_writer()):
                # link to parser and writer
                self.__bibparser = bibparser
                # why do we need the writer?
                self.__bibwriter = bibwriter
        except:
            log.error("No proper bibtex parser/writer provided. Fall back to standard one.")
            log.error(bibtex)

            self.__bibparser = bibtexparser.bibparser.BibTexParser()
            self.__bibwriter = bibtexparser.bibwriter.BibTexWriter()
        
        self.iddb = "tempID"
        self.bibtex = bibtex
        self.pdfFile = pdfFile
        self.abstract = abstract
        self.summary = summary
        self.date = datetime.date.today()
        self.printed = 0
        self.paperType = 0 # 0 misc, 1 theoretic, 2 application, 3 theory and application, 4 book, 5 Standard
        self.topic = 0
        self.favorite = 0
        self.citing = ""
        self.addKeyword(keywords)

                           
    # getter/setter function for bibtex
    @property
    def bibtex(self):
        return self.__bibwriter.write(self.__bibtex)

    @bibtex.setter
    def bibtex(self,bibtexstr):
        # is this needed?
        bibtexstr = str(replaceChars2(bibtexstr))
        # # remove " everywhere
        # bibtexstr = re.sub('(")(.*)(")([,]|\s)', '{\g<2>}\g<4>', bibtexstr)
        # get the parsed entry
        bibtex = self.__bibparser.parse(bibtexstr)
        if bibtex is None:
            log.warning("Bibtex not parsed properly: " + bibtexstr )
            self.__bibtex = {'ID': 'doe2013',
                            'ENTRYTYPE': 'misc'}
            return False

        else:
            self.__bibtex = bibtex
            # Remove keywords from bibtex
            self.__bibtex.pop('keyword', None)
            
            # Extract abstract from bibtex
            abstract = self.__bibtex.pop('abstract', None)
            if abstract is not None:
                self.abstract = abstract

            return True

        
    ## getter and setter methods for bibtex fields

    # general fields
    def getBibinfo(self,tag):
        if tag in self.__bibtex:
            if tag == 'author':
                seperator = " and "
                return seperator.join(self.__bibtex['author'])
            else:
                return str(self.__bibtex[tag])
        else:
            return ""
    def setBibinfo(self,tag,text):
        log.debug("We set the key " + tag + " of the bibtex to: " + text)
        self.__bibtex = self.__bibparser.set_entry_field(self.__bibtex,tag,text)
        log.debug("New bibtex is: " + str(self.__bibtex[tag]))
        
    # Type
    @property
    def bibType(self):
        return self.__bibtex["ENTRYTYPE"]
    @bibType.setter
    def bibType(self,entryId):
        self.__bibtex["ENTRYTYPE"] = entryId
    

    # setter/getter for title
    @property
    def title(self):
        if 'title' in self.__bibtex:
            return self.__bibtex['title']
        else:
            return ""
    @title.setter
    def title(self,title):
        self.__bibtex = self.__bibparser.set_entry_field(self.__bibtex,'title',title)

    #id
    @property
    def entryId(self):
        return self.__bibtex['ID']
    @entryId.setter
    def entryId(self,entryId):
        self.__bibtex["ID"] = entryId
    
    
    # Author
    @property
    def author(self):
        if 'author' in self.__bibtex:
            seperator = " and "
            return seperator.join(self.__bibtex['author'])
        else:
            log.debug("author not recognised in: " + self.__bibtex['ID'])
            return ""
    @author.setter
    def author(self,author):
        self.__bibtex = self.__bibparser.set_entry_field(self.__bibtex,'author',author)
        
    @property
    def year(self):
        if 'year' in self.__bibtex:
            return self.__bibtex['year']
        else:
            return None
    @year.setter
    def year(self,year):
        self.__bibtex = self.__bibparser.set_entry_field(self.__bibtex,'year',year)

    @property
    def journal(self):
        if 'journal' in self.__bibtex:
            return self.__bibtex['journal']
        else:
            return None
    @journal.setter
    def journal(self,test):
        self.__bibtex = self.__bibparser.set_entry_field(self.__bibtex,'journal',test)

    @property
    def booktitle(self):
        if 'booktitle' in self.__bibtex:
            return self.__bibtex['booktitle']
        else:
            return None
    @booktitle.setter
    def booktitle(self,booktitle):
        self.__bibtex = self.__bibparser.set_entry_field(self.__bibtex,'booktitle',booktitle)


    # link2pdf: not properly working.
    @property
    def link2pdf(self):
        if 'url' in self.__bibtex:
            return self.__bibtex['url']
        else:
            return "we will find it one day"
    @link2pdf.setter
    def link2pdf(self, link2pdf):
        link2pdf = link2pdf.strip()
        self.__bibtex['url']  = link2pdf

    # set functions:
    def updateIddb(self,idtext):
        self.iddb = idtext

    def addKeyword(self, keywords):
    
        if isinstance(keywords,str):
            self.keywords = re.split(' *, *', keywords.lower())
        idxToDelete = []
        for kwdIdx,kwd in enumerate(self.keywords): # Find empty indexes and delete those
            if len(kwd) is 0:
                idxToDelete.append(kwdIdx)
        for idx in reversed(idxToDelete): 
            del(self.keywords[idx])

    def updatePdfFile(self,pdfFile):
        self.pdfFile = pdfFile.strip()

    def updateAbstract(self,abstract):
        self.abstract = abstract.lstrip().rstrip() + '\n' # remove trialing and preceding newline

    def updateSummary(self,summary):
        self.summary = summary

    def addCiting(self,citing):
        self.citing = citing.strip()

    def setPaperType(self,paperType):
        if not isinstance(paperType,int):
            raise TypeError("paperType must be of type int")
        else:
            self.paperType = paperType

    def setTopic(self,topic):
        if not isinstance(topic,int):
            raise TypeError("topic must be of type int")
        else:
            self.topic = topic

    def setFavorite(self,state):
        if not isinstance(state,int):
            raise TypeError("state must be of type int")
        elif state < 0 or state > 1:
            raise ValueError("state must be 0 or 1")
        else:
            self.favorite = int(state)

    def setPrinted(self,state):
        if not isinstance(state,int):
            raise TypeError("state must be of type int")
        elif state < 0 or state > 1:
            raise ValueError("state must be 0 or 1")
        else:
            self.printed = int(state)

           
    def setBibtexSceleton(self,bibtex): 
        # Used only to put in a BibTex sceleton. This prevents the clearing from the other fields
        self.bibtex = bibtex.lstrip().rstrip() + '\n' # to remove trialing and leading whitespaces and put one in the end

        if 'author' in self.__bibtex:
            self.author = self.__bibtex['author']

        if 'year' in self.__bibtex:
            self.year = self.__bibtex['year']

        if 'journal' in self.__bibtex:
            self.journal = self.__bibtex['journal']

    


