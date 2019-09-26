# -*- coding: utf-8 -*-
import re ,datetime, types, socket
import paperdb.entryBase 

class Entry(paperdb.entryBase.Entry):

    def __init__(self, bibtex, bibparser, bibwriter, pdfFile = "paperdb/test.pdf", keywords = "blob,blab,house", abstract = "Investigate the Blab in different areas of the house.", summary = "The Blab can be in a lot of different places."):

        paperdb.entryBase.Entry.__init__(self,bibtex,bibparser,bibwriter,pdfFile,keywords,abstract,summary)
        hostName = re.search("[A-Za-z0-9]*", socket.gethostname())
 
        self.iddb = "tmpID" + hostName.group(0)
                

    ## More debugging and deprecated functions
    def printEntry(self):
        print('ID: ' + self.entryId + '\nTitle: ' + self.title +'\npdfFile: ' + self.pdfFile)
        for word in self.keywords:
            print('Keyword: ' + word)
        print('Abstract: ' + self.abstract + '\nSummary: ' + self.summary + '\nLink2PDF: ' + self.link2pdf + '\nBibTex: ' + self.bibtex + '\nUpdated: ' + self.date + '\nPrinted: ' + self.printed + '\nType: ' + self.paperType + '\nCiting: ' + self.citing)
        print('Author: ' + self.author + '\nYear: ' + self.year + '\nJournal: ' + self.journal + '\nFavorite: ' + self.favorite)
        print('%%%%%%%%\n\n\n')


    def printToXML(self):
        
        xmlString = """<entry>     
\t<id>%(ID)s</id>
\t<inPaperform>%(PAPERFORM)d</inPaperform>
\t<title>%(TITLE)s</title>
\t<pdfFilePath>%(PDFPATH)s</pdfFilePath>
%(KEYWORDS)s\t<abstract>%(ABSTRACT)s</abstract>
\t<summary>%(SUMMARY)s</summary>
\t<linkToPdf>%(LINKTOPDF)s</linkToPdf>
\t<bibTex>%(BIBTEX)s</bibTex>
\t<paperType>%(PAPERTYPE)d</paperType>
\t<citing>%(CITING)s</citing>
\t<author>%(AUTHOR)s</author>
\t<year>%(YEAR)s</year>
\t<journal>%(JOURNAL)s</journal>
\t<favorite>%(FAVORITE)d</favorite>
\t<updated>%(UPDATED)s</updated>
</entry>"""

        keywordStr = ""
        for keyword in self.keywords:
            keywordStr += "\t<stichwort>%s</stichwort>\n" %self.escape(keyword)

        xmlFinal = xmlString %{
            'ID' : self.escape(self.entryId),
            'TITLE' : self.escape(self.title),
            'PDFPATH' : self.escape(self.pdfFile),
            'KEYWORDS' : keywordStr,
            'ABSTRACT' : self.escape(self.abstract),
            'SUMMARY' : self.escape(self.summary),
            'LINKTOPDF' : self.escape(self.link2pdf),
            'BIBTEX' : self.escape(self.bibtex),
            'UPDATED' : str(datetime.date.today()),
            'PAPERFORM' : self.printed,
            'PAPERTYPE' : self.paperType,
            'CITING' : self.citing,
            'AUTHOR' : self.author,
            'YEAR' : self.year,
            'JOURNAL' : self.journal,
            'FAVORITE' : self.favorite
        }

        print(xmlFinal)
        # pyperclip.copy(xmlFinal)

