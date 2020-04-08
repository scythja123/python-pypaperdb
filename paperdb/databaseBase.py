#! /usr/bin/env python
from paperdb.entryBase import Entry
import sys,os
import re ,datetime, socket
import logging
log =logging.getLogger(__name__)

import bibtexparser
from bibtexparser.bibDefinitions import BibDefinitions
import custom

if __name__ == "__main__":
    # Someone launches this class directly
    log.error("please run application to start Paperdatabase")

        
class Database():
    """This class provides the main functions for database handling. Some of the functions might have to be updated to work with specific database files.

    Public functions:

    getAllEntries(): returns a list with all entries in the database
    searchEntry(id): returns the entry with ID id
    existsid(id): returns true if an entry with ID id exists
    getEntries(keywords)
    appendBibtex(keywords,fileName)
    exportBibtex(keywords,fileName)   
    store(dbentry,tag,value)
    save(entry)
    remove(id)
    getKeywords()

    Attributes: 
    basePath
    dbFile

    """
    
    # make this better
    charmap2 = {'<br>': '\n'}
    #replaceChars = lambda self, myStr: str.join('',[self.charmap.get(c,c) for c in str(myStr)])

    def replaceChars2(self,text):
        for key in self.charmap2:
            text = text.replace(key, self.charmap2[key])
        return text
    # ----

    # what is this for?
    basePath = "bla"
    _kwdlist = "basic,test"
    
    def __init__(self,dbFilePath):
        self.basePath = os.path.dirname(dbFilePath)
        self.dbFile = dbFilePath

        # set up the bibtex parser: 
        self.init_bibparser()

            
    def searchEntry(self,searchid):
        log.error("searchEntry not yet implemented, returns a dummy entry")
        return Entry("@misc{test1,author={Test. A}",self.__bibparser,self.__bibwriter)

    def existsid(self,searchid):
        log.error("existsid not yet implemented. returns True if id is yes, False otherwise")
        if(searchid=="yes"):
            return True
        else:
            return False

    def getAllTopics(self):
        log.error("getAllTopics not yet implemented. returns a sorted list of topics")
        return list()

    def getAllEntryTypes(self):
        log.error("getAllEntryTypes not yet implemented. returns a sorted list of entryTypes")
        return list()

    def addTopic(self,topic):
        log.error("addTopic not yet implemented. adds a topic to the database")

    def addEntryType(self,entryType):
        log.error("addEntryType not yet implemented. adds a entryType to the database")

    def removeTopic(self,topic):
        log.error("removeTopic not yet implemented. remove a topic to the database")

    def removeEntryType(self,entryType):
        log.error("removeEntryType not yet implemented. remove a entryType to the database")
                
    def getAllEntries(self): 
        log.error("getAllEntries not yet implemented. returns two base entries")
        entries =[]
        entries.append(Entry("@misc{test1,author={Test. A}",self.__bibparser,self.__bibwriter))
        entries.append(Entry("@misc{test2,author={Test. A}",self.__bibparser,self.__bibwriter))
        return entries

    def getFirstEntries(self,number):
        log.error("getFirstEntries not yet implemented. returns two base entries")
        entries =[]
        entries.append(Entry("@misc{test1,author={Test. A}",self.__bibparser,self.__bibwriter))
        entries.append(Entry("@misc{test2,author={Test. A}",self.__bibparser,self.__bibwriter))
        return entries
        
    def getEntries(self,keywords): 
        log.error("getEntries not yet implemented. returns two base entries")
        entries =[]
        entries.append(Entry("@misc{test1,author={Test. A},",self.__bibparser,self.__bibwriter))
        entries.append(Entry("@misc{test2,author={Test. A},",self.__bibparser,self.__bibwriter))
        return entries

    def getKeywords(self,user = None):
        kwdlist = self._kwdlist

        uniquekwdlist = []
        for kwd in kwdlist:
            if kwd not in uniquekwdlist:
                uniquekwdlist.append(kwd)
        
        return uniquekwdlist

    def exportBibtex(self,keywords,fileName,options=None):
        if keywords ==[]:
            entries = self.getAllEntries()
        else:
            entries = self.getEntries(keywords)

        self.process_print_options(options)

        bibtex=""
        for entry in entries:
            bibtex = bibtex + entry.export_bibtex(self.__external_writer) + "\n"
        
        #write to file
        bibfile = open(fileName,'w',encoding='utf-8')
        bibfile.write(bibtex)
        bibfile.close()

        self.init_external_print()

        return bibtex

    def appendBibtex(self,keywords,fileName,options=None):
        if keywords ==[]:
            entries = self.getAllEntries()
        else:
            entries = self.getEntries(keywords)

        self.process_print_options(options)

        bibtex=""
        for entry in entries:
            bibtex = bibtex + self.replaceChars2(entry.export_bibtex(self.__external_writer)) + "\n"
        
        #write to file
        bibfile = open(fileName,'a',encoding='utf-8')
        bibfile.write(bibtex)
        bibfile.close()

        self.init_external_print()
        
        return bibtex

    def writeBibtexFromAux(self,inputfile,options=None,outputfile=None):
        savePath = os.path.dirname(inputfile)

        # process the aux file
        auxfile = open(inputfile, 'r')

        indexesToExport = set([])
        for line in auxfile:
            if(re.search('(citation{)(.*)(})', line)):
                ids = re.search('(citation{)(.*)(})', line)
                ids = ids.group(2)
                ids = re.split(' *, *',ids)
                for index in ids:
                    if(index != "biblatex-control"):
                        indexesToExport.add(index)

            if not outputfile:
                if(re.search('(bibdata{)(.*)(})', line)):
                    bibfilenames = re.search('(bibdata{)(.*)(})', line)
                    bibfilenames = bibfilenames.group(2)
                    bibfilenames = re.split(' *, *',bibfilenames)
                    if(bibfilenames[0].endswith("blx")):
                        bibfilename = '.'.join([bibfilenames[1],'bib'])
                    else:
                        bibfilename = '.'.join([bibfilenames[0],'bib'])
                    # print(bibfilename)
                    outputfile = os.path.join(savePath,bibfilename)
        
        auxfile.close()
        log.debug("I am writing bib File")
        
        # process options adapt the writer and change to external writer
        self.process_print_options(options)
               

        indexesNotFound = list()
        bibtex = ""
        for index in indexesToExport:
            if self.existsid(index):
                bibtex = bibtex + self.searchEntry(index).export_bibtex(self.__external_writer)  + "\n"
            else:
                indexesNotFound.append(index)
                log.debug(index + " not found in database")

        #print(bibtex)
        bibfile = open(outputfile,'w',encoding='utf-8')
        bibfile.write(bibtex)

        if len(indexesNotFound)>0:
            log.warning("I didn't find bitex entries for\n" + "\n".join(indexesNotFound))

            
        log.info(str(len(indexesToExport)-len(indexesNotFound)) + "/" + str(len(indexesToExport)) + " BibTex entries written to " + outputfile)               
        bibfile.close()

        self.init_external_print()
        
    
    def store(self,dbentry,tag,value):
        log.error("store not yet implemented")

    def save(self,entry):
        log.error("save not yet implemented")

    def remove(self,id):
        log.error("remove not yet implemented")


    def init_bibparser(self):
        # define the behaviour of the writer and parser:
        BibDefinitions.reset()   
        BibDefinitions.add_containing_latex_fields(str.split(custom.config.get('bibtex','latex_strings'),','))
        BibDefinitions.add_protected_upper_case_fields(str.split(custom.config.get('bibtex','protect_uppercase_strings'),','))
        BibDefinitions.add_protected_upper_case_words(str.split(custom.config.get('bibtex','customCapitalisation'),','))
        
        # select which fields are internally not strings.
        internally_stored = str.split(custom.config.get('bibtex','internally_stored'),',')

        for field in internally_stored:
            standard = ['']
            recognised = dict()
            listing = dict(custom.config.items('strings_'+field.strip()))
            index = 0
            for key in listing:
                index = index + 1
                standard.append(key)
                possibilities = str.split(listing[key],';')
                for item in possibilities:
                    val = item.lower()
                    val = val.lstrip().rstrip()
                    recognised[val] = index
            BibDefinitions.add_stored_as_integer(field,recognised,standard)

        # make the parser
        self.__bibparser = bibtexparser.bibparser.BibTexParser()
        self.__bibparser.overwrite_key_replacements(dict(custom.config.items('key_replacements')))

        # make the writer for internal printing:
        self.__bibwriter = bibtexparser.bibwriter.BibTexWriter()
        self.__bibwriter.display_order = str.split(custom.config.get('bibtex','displayOrder'),',')

        
        self.__external_writer = bibtexparser.bibwriter.BibTexWriter()
        self.init_external_print()

    def init_external_print(self):
        self.__external_writer.indent = '  '
        self.__external_writer.display_order = str.split(custom.config.get('write_bibtex','displayOrder'),',')
        self.__external_writer.set_do_not_display_field(str.split(custom.config.get('write_bibtex','excludedTags'),','))

    def process_print_options(self,options):
        if options is not None:
            if 'excludedTags' in options:
                self.__external_writer.add_do_not_display_field(options['excludedTags'])
            if 'includedTags' in options:
                self.__external_writer.do_only_display_fields = options['includedTags']
            if 'month_as_string' in options:
                self.__external_writer.add_write_as_string_field('month',options['month_as_string'])

    def get_non_recognised_string_fields(self,field):
        return BibDefinitions.get_non_recognised_string_fields(field)

    def getNewEmptyEntry(self):
        return Entry("@misc{text,author={Test. A},}",self.__bibparser,self.__bibwriter)
