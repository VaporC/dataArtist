# from Colors import Colors
from ErrorBar import ErrorBar
from Legend import Legend
from PlotStyle import PlotStyle
# from LineWidth import LineWidth
# from SymbolColor import SymbolColor
# from Symbols import Symbols
from dataArtist.figures.image.tools.view.Axes import Axes
from dataArtist.figures.image.tools.view.LockView import LockView
from dataArtist.figures.image.tools.general.Reload import Reload

# from LinkView import LinkView
from Table import Table

color = 'blue'
show = True
tools = (Reload, LockView,Axes,Legend, PlotStyle,ErrorBar)