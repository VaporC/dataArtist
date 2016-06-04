#!/usr/bin/env python
"""
run dataArist from taskbar
"""

import sys
from dataArtist import gui

sys.argv.append('-s')

gui.main()
