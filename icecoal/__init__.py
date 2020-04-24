"""
Light weight SQL database
Usage::
    >>> from icecoal import query
    >>> result=query("select name from input.csv,heads.csv where native='usa'")
"""

from .icecoal import query

__all__ = ('query')