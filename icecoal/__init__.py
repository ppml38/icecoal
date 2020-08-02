"""
Light weight SQL database
Usage::
    >>> from icecoal import query
    >>> result=query("select name from input.csv,heads.csv where native='usa'")
"""

from .icecoal import query,escape
from .utilfuns import setdel,getdel

__all__=['query','setdel','getdel','escape']