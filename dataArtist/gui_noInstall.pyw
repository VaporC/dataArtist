#!/usr/bin/env python
"""start dataArtist with this module if other modules are in same
root folder but not globally installed
"""

PROFILE_IMPORT_SPEED = False


if PROFILE_IMPORT_SPEED:
    import cProfile, pstats
    pr = cProfile.Profile()
    pr.enable()


import sys
import os


#main directory for all code:
pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(os.curdir)))
print os.path.abspath(os.curdir)
for s in os.listdir(pkg_dir):
    #add local code to sys.path
    f = os.path.join(pkg_dir, s)
    if os.path.isdir(f):
        print f
        sys.path.insert(0,f)


from dataArtist import gui

if PROFILE_IMPORT_SPEED:
    pr.disable()
    s = pstats.Stats(pr)
    s.sort_stats('cumtime').print_stats(500)

gui.main()
