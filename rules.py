from enum import Enum
from typing import NamedTuple


class BNFPreDefined(Enum):
    Number = r"[0-9][_0-9]*(\.[0-9][_0-9]*)?"
    String = r"[a-z0-9]*(\"(?:\\.|[^\\\"])*\"|\'(?:\\.|[^\\'])*\')"
    Bool = r"(true)|(false)"
    Symbol = r"([a-zA-Z_][a-zA-Z0-9_]*)|\$"
    Assign = r"=|(\*=)|(\%=)|(\^=)|(\+=)|(-=)|(/=)"
    Binop = r"\+|-|\*|\/|\^|\%|\.{2}|(<=)|<|(>=)|>|(==)|(!=)|(and)|(or)"
    Unop = r"-|(not)"
    Equal = r"="
    # Multiply = r"\*="
    # Modulate = r"\%="
    # Exponate = r"\^="
    # Add = r"\+="
    # Subtract = "-="
    # Divide = "/="
    # E = r"^$"
    Type = r"(number)|(string)|(list)|(bool)"
    Colon = r":"
    Dot = r"\."
    FieldSeperator = r","
    OpenBracket = r"\("
    OpenSquareBracket = r"\["
    OpenCurlyBracket = r"\{"
    CloseBracket = r"\)"
    CloseSquareBracket = r"\]"
    CloseCurlyBracket = r"\}"
    StatementSeperator = r"[\n;]"


class BNFRules(Enum):
    Flag = "--!"
    Comment = "//"
    Assign = "::="
    CurlyBrackets = r"(?<!\")\{(.*?)\}(?!\")"
    SquareBrackets = r"(?<!\")\[(.*?)\](?!\")"
    Rule = r"<\w*>"
    StringLiteral = r"[a-z0-9]*(\"(?:\\.|[^\\\"])*\"|\'(?:\\.|[^\\'])*\')"
    # Symbol = r"<([a-zA-Z_][a-zA-Z0-9_]*)>|<\$>"

    Pipe = r"\|"
    StatementSeperator = r"[\n]+"


class Keywords(Enum):
    NoRefresh = r"^(norefresh)$"
    Define = r"^(define)$"
    ElseIf = r"^(elseif)$"
    Return = r"^(return)$"
    Shared = r"^(shared)$"
    While = r"^(while)$"
    Break = r"^(break)$"
    Else = r"^(else)$"
    For = r"^(for)$"
    Var = r"^(var)$"
    Not = r"^(not)$"
    Let = r"^(let)$"
    If = r"^(if)$"
    In = r"^(in)$"


class CompilerRules(Enum):
    Flag = "--!"
    Comment = "//"

    StringLiteral = r"[a-z0-9]*(\"(?:\\.|[^\\\"])*\"|\'(?:\\.|[^\\'])*\')"

    NoRefresh = r"^(norefresh)$"
    Define = r"^(define)$"
    ElseIf = r"^(elseif)$"
    Return = r"^(return)$"
    Shared = r"^(shared)$"
    While = r"^(while)$"
    Break = r"^(break)$"
    Else = r"^(else)$"
    For = r"^(for)$"
    Var = r"^(var)$"
    Not = r"^(not)$"
    Let = r"^(let)$"
    If = r"^(if)$"
    In = r"^(in)$"

    Symbol = r"([a-zA-Z_][a-zA-Z0-9_]*)|\$"
    Number = r"[0-9][_0-9]*(\.[0-9][_0-9]*)?"

    # operators
    Multiply = r"\*="
    Modulate = r"\%="
    Exponate = r"\^="
    Add = r"\+="
    Subtract = "-="
    Divide = "/="

    Equal = "=="
    NotEqual = "!="
    MoreOrEqual = ">="
    LessOrEqual = "<="
    MoreThan = ">"
    LessThan = "<"

    Assign = "="

    # maths operators
    Modulo = r"\%"
    Power = r"\^"
    Star = r"\*"
    Slash = "/"
    Plus = r"\+"
    Minus = "-"


    # terminator
    Colon = ":"
    Comma = ","
    Dot = r"\."
    StringJoin = r"\.{2}"
    OpenBracket = r"\("
    OpenSquareBracket = r"\["
    OpenCurlyBracket = "{"
    CloseBracket = r"\)"
    CloseSquareBracket = r"\]"
    CloseCurlyBracket = "}"
    StatementSeperator = r"\n"


RuleType = BNFRules | CompilerRules | BNFPreDefined | Keywords
OptionalStr = str | None
Token = NamedTuple("Token", (("token_type", RuleType), ("token_str", str), ("location", tuple[int, int])))
Rule = NamedTuple("Rule", (("rule", str), ("optional", str)))
IncompleteRules = list[list[list[Rule]]]
