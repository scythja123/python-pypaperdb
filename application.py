#!/usr/bin/env python
# The QT application handling the program and events.

import sys,os
from PyQt5 import QtGui
from PyQt5 import QtWidgets
import configparser
import argparse
import re
import logging 
log = logging.getLogger(__name__)

import custom

# import paperdb
import gui.overview as mainwindow

#import cProfile

def CheckExt(choices):
    # Used in argparser to check for file extensions
    class Act(argparse.Action):
        def __call__(self,parser,namespace,fname,option_string=None):
            ext = os.path.splitext(fname)[1][1:]
            if ext not in choices:
                option_string = '({})'.format(option_string) if option_string else ''
                parser.error("{} requires files ending with {}".format(option_string,choices))
            else:
                setattr(namespace,self.dest,fname)

    return Act


def argumentParser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("database",nargs="?",help="Open specified database file")
    argparser.add_argument("--get_bibtex",help="Get the bibliography for the .aux file specified",metavar="FILENAME", action=CheckExt({'aux'}))
    argparser.add_argument("--bibname",help="Specify custom name for the output bibliography", metavar="FILENAME")
    arggroup = argparser.add_mutually_exclusive_group()
    arggroup.add_argument("--exclude_attr", help="Excludes list of BibTex tags provided. If empty argument is provided, use all arguments. When argument is omitted, the defaults from the cfg are used. Can not be used together with --include-attr", nargs="?", default=argparse.SUPPRESS)
    arggroup.add_argument("--include_attr", help="Only the list of provided tags are included.  Can not be used together with --exclude-attr.", nargs="?", default=argparse.SUPPRESS)
    argparser.add_argument("-v","--verbose", help="Verbose output. -vv, -vvv for increased verbosity.",action="count", default=0)

    return argparser


def getConfig(filePath):
    # read config files:
    cfgFile = 'pypaperdb.cfg'
    #config = configparser.ConfigParser()
    config = configparser.RawConfigParser()
    config.optionxform = str
    
    # check in ~ for configfile
    try:
        config.read_file(open(os.path.expanduser('~/.pypaperdb.cfg')))
    except IOError:
        log.info('User cfg not found: Loading default cfg')
        config.read_file(open(filePath[0] + '/pypaperdb.cfg'))

    cfgPath = filePath[0] + '/config'
    cfgFiles = []
    for file in os.listdir(cfgPath):
        if file.endswith('.cfg'):
            cfgFiles.append(os.path.join(cfgPath,file))

    config.read(cfgFiles)

    return config

def openDatabase():
    if not custom.args.database:
        dbFile = custom.config.get('user','dbFile')
        db = custom.config.get('user','database')
    else:
        dbFile = custom.args.database
        db = "xmldb"            # TODO read this from the mimetype or filetype
        
    dbFileAbsPath = os.path.expanduser(dbFile)
    dbFileAbsPath = os.path.realpath(dbFileAbsPath)
    log.info(dbFileAbsPath)
    # create data base: check which one to use from config files
        
    if db == "dummydb":
        log.info(db)
        import paperdb.dummydb as database
    elif db =="base":
        log.info(db)
        import paperdb.databaseBase as database
    elif db == "xmldb":
        log.info(db)
        log.info(dbFileAbsPath)
        import paperdb.xmldb as database
    elif db == "none":
        log.warning("No database imported.\n")
  
    # cProfile.run('database = database.Database(dbFileAbsPath)')
    return database.Database(dbFileAbsPath)

def getBibtex():
    # TODO: check if the aux file exists

    # Check if we have include only or exclude only tags       
    
    includedTags = ()
    excludedTags = ()
    if not (hasattr(custom.args,'include_attr') or hasattr(custom.args,'exclude_attr')):
        try:
            # These go in pypaperdb.cfg as bibtexExcludedFields = url =, author =,...
            excludedTags = tuple(custom.config.get('write_bibtex','bibtexExcludedFields').split(','))
        except:
            excludedTags = tuple()
            print("No bibtexExcludedFields defined under [write_bibtex] in pypaperdb.cfg")
        # Let's check if we need to include or exclude some tags. 
    elif hasattr(custom.args,'include_attr'):
        if custom.args.include_attr is not None:
            includedTags = tuple(re.split(' , |, | ,|,| ', custom.args.include_attr))             
    elif hasattr(custom.args,'exclude_attr'):
        if custom.args.exclude_attr is not None: # if this is None it just means that we want to overide the config default
            excludedTags = tuple(re.split(' , |, | ,|,| ', custom.args.exclude_attr))

    log.info("excludedTags: " +  ", ".join(excludedTags))
    log.info("includedTags: " +  ", ".join(includedTags)) # not sure what this should
    options = {'excludedTags': excludedTags, 'includedTags':includedTags}

    database.writeBibtexFromAux(custom.args.get_bibtex,options,custom.args.bibname)

    return 


def initLogging():
    if custom.args.verbose > 2:
        logging.getLogger('bibtexparser').setLevel(logging.DEBUG) # we are not interested in bibtex parser logging messages
    else:
        logging.getLogger('bibtexparser').setLevel(logging.WARNING) # we are interested in bibtex parser logging messages

    logLevels = (logging.WARNING ,logging.INFO ,logging.DEBUG)
    logging.basicConfig(level=logLevels[min(len(logLevels)-1,custom.args.verbose)])

    return

if __name__ == "__main__":
    # Someone launches this class directly
    
    # Let's first check if command line arguments are provided
    custom.args = argumentParser().parse_args()

    # set up the logger verbosity
    initLogging()
    
    filePath = os.path.split(os.path.realpath(__file__))  # get path of application file, also when called from symlink 

    custom.config = getConfig(filePath) # load configs

    # Create the QApplication with the main window
    app = QtWidgets.QApplication(sys.argv)

    # Before opening the GUI, let's check if we have some command line arguments that we want to parse
    current_database = openDatabase() # load the database and the right backend

    if custom.args.get_bibtex:
        # Just export a bibtex file and quit
        getBibtex()
        exit()

    #cProfile.run('mainWindow = mainwindow.OverviewWindow(database,config)')
    mainWindow = mainwindow.OverviewWindow(current_database)
    mainWindow.setWindowIcon(QtGui.QIcon(filePath[0] + '/paper-plane')) # Icon made by Madebyoliver, http://www.flaticon.com/authors/madebyoliver from www.flaticon.com  Remember to credit
    mainWindow.show()

    # enter the main loop
    app.exec()

