from LensDistortion import LensDistortion
from RelativeSharpness import RelativeSharpness
from FlatField import FlatField
from DarkCurrent import DarkCurrent
from NoiseLevelFunction import NoiseLevelFunction
from PointSpreadFunction import PointSpreadFunction
from DeconvolutionBalance import DeconvolutionBalance

tools = ( RelativeSharpness, NoiseLevelFunction, 
          DarkCurrent, FlatField, PointSpreadFunction, 
          DeconvolutionBalance, LensDistortion )
position='top'
secondRow=True
color='pink'
show = {'simple':False, 'electroluminescence':True}

