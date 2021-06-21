#!/usr/bin/env python3
# Original Author    : Edwin G. W. Peters @ epeters
#   Creation date    : Mon Jun 21 15:49:55 2021 (+1000)
#   Email            : edwin.peters@unsw.edu.au
# ------------------------------------------------------------------------------
# Last-Updated       : Mon Jun 21 16:17:37 2021 (+1000)
#           By       : Edwin G. W. Peters @ epeters
# ------------------------------------------------------------------------------
# File Name          : pypaperdb.py
# Description        : 
# ------------------------------------------------------------------------------
# Copyright          : Insert license
# ------------------------------------------------------------------------------

import sys,os
file_path = os.path.split(os.path.realpath(__file__))[0]
sys.path.append(file_path)
#print(file_path)
#sys.path.append("home/epeters/.scripts/paper_database_prog/")
import pypaperdb

pypaperdb.start()
