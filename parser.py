"""
  _    _ _____ _ 
 | |  | |_   _| |
 | |__| | | | | |
 |  __  | | | | |
 | |  | |_| |_|_|
 |_|  |_|_____(_)
               
THIS WORKS FOR <Scratch 3.29.1> ONLY. 
FUTURE/PAST VERSIONS *MAY* WORK BUT NO PROMISES!
"""

from __future__ import annotations
import sys
from tokenizer import Compiler
from contextlib import contextmanager
    

# many thanks:
# https://stackoverflow.com/questions/38598740/raising-errors-without-traceback
@contextmanager
def disable_traceback():
    """
    All traceback information is suppressed and only the exception type and value are printed
    """
    default_value = getattr(sys, "tracebacklimit", 1000)  # `1000` is Python's default value
    sys.tracebacklimit = 0
    yield
    sys.tracebacklimit = default_value  # revert changes


# with help from
# https://github.com/Spu7Nix/SPWN-language/blob/master/parser/src/parser.rs

# note that for break and continue there'll need to be some funky things needed:
# https://scratch.mit.edu/discuss/topic/255234/?page=1


if __name__ == "__main__":
    compiler = Compiler("small_test.itch", "itch_grammar.bnf")
    compiler.compile()
