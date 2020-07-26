import re, configparser
import paperdb.entry as entry
import paperdb.pyperclip as pyperclip
import datetime
import paperdb.databaseBase

class Database(paperdb.databaseBase.Database):
    
    charmap = {'\n': '<br>'}
    replaceChars = lambda self, myStr: str.join(u'',[self.charmap.get(c,c) for c in str(myStr)])
    charNewline = {'\n': ' '}
    removeNewline = lambda self, myStr: str.join(u'',[self.charNewline.get(c,c) for c in str(myStr)])

    def __init__(self,dbfile):
        paperdb.databaseBase.Database.__init__(self,dbfile)
        self.dbfile = dbfile

    def save(self,entry):
        
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
        for keyword in entry.keywords:
            keywordStr += "\t<stichwort>%s</stichwort>\n" %entry.escape(keyword)

        xmlFinal = xmlString %{
            'ID' : entry.escape(entry.id),
            'TITLE' : entry.escape(entry.title),
            'PDFPATH' : entry.escape(entry.pdfFile),
            'KEYWORDS' : keywordStr,
            'ABSTRACT' : entry.escape(entry.abstract),
            'SUMMARY' : entry.escape(entry.summary),
            'LINKTOPDF' : entry.escape(entry.link2pdf),
            'BIBTEX' : entry.escape(entry.bibtex),
            'UPDATED' : str(datetime.date.today()),
            'PAPERFORM' : entry.printed,
            'PAPERTYPE' : entry.paperType,
            'CITING' : entry.citing,
            'AUTHOR' : entry.author,
            'YEAR' : entry.year,
            'JOURNAL' : entry.journal,
            'FAVORITE' : entry.favorite
        }

        print(xmlFinal)
        pyperclip.copy(xmlFinal)


if __name__ == "__main__":

    from PyQt4 import QtCore
    
    entry = entry.Entry()
    db = Database()
    
    bibtex = """@INPROCEEDINGS{4550808, 
author={Jianping Song and Song Han and Mok, A.K. and Deji Chen and Lucas, M. and Nixon, M.}, 
booktitle={Real-Time and Embedded Technology and Applications Symposium, 2008. RTAS '08. IEEE}, 
title={WirelessHART: Applying Wireless Technology in Real-Time Industrial Process Control}, 
year={2008}, 
month={April}, 
pages={377-386}, 
keywords={process control;time division multiple access;wireless LAN;2.4 GHz ISM radio band;TDMA based wireless mesh networking technology;WirelessHART network;central network manager;communication security;industrial process control;network wide synchronization;wireless technology;Buildings;Communication standards;Communication system control;Communication system security;Industrial control;Measurement standards;Process control;Process design;Prototypes;Wireless communication;Process Control;Security;Synchronization;WirelessHART}, 
doi={10.1109/RTAS.2008.15}, 
ISSN={1545-3421},}"""

    entry.updateBibtex(QtCore.QString(bibtex),True)
    entry.addKeyword('hest')
    
    
    db.save(entry)
