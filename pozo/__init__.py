from .data import Data
from .axes import Axis
from .tracks import Track
from .graphs import Graph
from .units import LasRegistry

def deLASio(curve):
    return curve.mnemonic.split(":", 1)[0] if ":" in curve.mnemonic else curve.mnemonic

units = LasRegistry()
units.define('Gamma_Ray_API = [Gamma_Ray_Tool_Response]  = gAPI = GAPI') # TODO these aren't correct
units.define("Porosity_Units= [Volume] / [Volumne] = pu = PU") # TODO these aren't correct
units.add_las_map('DEPT', 'M'   , 'meter', "HIGH")
units.add_las_map('GR'  , 'GAPI', 'gAPI', "HIGH")
units.add_las_map('CGR' , 'GAPI', 'gAPI', "HIGH")
units.add_las_map('CALI', 'CM'  , 'centimeter', "HIGH")
units.add_las_map('DRHO', 'G/C3', 'gram / centimeter ** 3', "HIGH")
units.add_las_map('RHOB', 'G/C3', 'gram / centimeter ** 3', "HIGH")
units.add_las_map('DT'  , 'US/F', 'microsecond / foot', "HIGH")
units.add_las_map('ILD' , 'OHMM', 'ohm * meter', "HIGH")
units.add_las_map('LLD' , 'OHMM', 'ohm * meter', "HIGH")
units.add_las_map('ILM' , 'OHMM', 'ohm * meter', "HIGH")
units.add_las_map('LLS' , 'OHMM', 'ohm * meter', "HIGH")
units.add_las_map('SFL' , 'OHMM', 'ohm * meter', "HIGH")
units.add_las_map('SGR' , 'GAPI', 'gAPI', "HIGH")
units.add_las_map('SP'  , 'MV'  , 'millivolt', "HIGH")
units.add_las_map('MSFL', 'OHMM', 'ohm * meter', "HIGH")
units.add_las_map('NPHI', 'PU'  , 'pu'                      , "- %, fraction, API? - LOW")
units.add_las_map('PEF' , ''    , 'percent'                 , "- %, fraction, ppm? - LOW")
units.add_las_map('POTA', ''    , 'percent'                 , "- %, fraction, ppm? - LOW")
units.add_las_map('THOR', ''    , 'percent'                 , "- %, fraction,  ppm? - LOW")
units.add_las_map('URAN', ''    , 'percent', "- %, fraction, ppm? - LOW")

# Error on dimensionless
