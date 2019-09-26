# import sys
from __future__ import print_function


def warning(*objs):
    print("Warning: ", *objs, file=sys.stderr)

def error(*objs):
    print("Error: ", *objs, file=sys.stderr)
