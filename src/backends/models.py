"""
This file contains definitions of data models to be used in search results.
"""

from dataclasses import dataclass
from typing import List


# Note the @dataclass decorator auto-generates necessary but trivial utility functions for 
#   simple data container classes like these.

@dataclass
class Match:
    line_number: int  # which line matched
    text: str         # content of the matched line


@dataclass
class FormattedResult:
    filename: str         # filename containing match
    repository: str       # repo containing the file
    matches: List[Match]  # all matching lines in the file
    url: str              # Sourcegraph URL at which file can be viewed
