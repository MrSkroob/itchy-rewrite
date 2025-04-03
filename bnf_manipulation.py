import re
# the reason why we don't have it in this file, is because it's really messy. 

# Thanks!
# https://github.com/somemarsupials/bnfparsing/blob/master/bnfparsing/utils.py

def head(string: str):
    """ Split a string into the first and following characters. If
    the string is empty or no string is passed, return None and the
    rest of the string.
    """
    return (string[0], string[1:]) if string else (None, string)


def is_quote(c: str):
    """ Verify a string as a quotation mark. True for single or double 
    quotes. Designed to work with strings of length 1. """
    return c in "'\""


def is_literal(c: str):
    """ Verify a string as a literal. True for strings surrounded by 
    double quotes. 
    """
    return c[0] == "'" and c[-1] == "'" and len(c) > 1


def de_string(c: str) -> str:
    return c[1:-1]


def split_tokens(text: str):
    """
    Splits a string by whitespace, but does NOT split substrings
    that are surrounded by single or double quotes.
    The outer quotes are stripped from the returned tokens.
    """
    # Pattern explanation:
    #   (".*?")  matches a double-quoted sequence (non-greedy)
    #   ('.*?')  matches a single-quoted sequence (non-greedy)
    #   (\S+)    matches sequences of non-whitespace (unquoted tokens)
    pattern = r'(".*?"|\'.*?\'|\S+)'
    
    # Find all matches (each match is either a quoted string or an unquoted chunk)
    matches: list[str] = re.findall(pattern, text)
    
    # Strip the surrounding quotes from quoted matches

    return matches
