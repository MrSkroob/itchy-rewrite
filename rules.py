from enum import Enum
from dataclasses import dataclass
from typing import NamedTuple, Callable


class BNFPreDefined(Enum):
    Number = r"[0-9][_0-9]*(\.[0-9][_0-9]*)?"
    String = r"[a-z0-9]*(\"(?:\\.|[^\\\"])*\"|\'(?:\\.|[^\\'])*\')"
    Bool = r"\b(true)|(false)\b"
    Symbol = r"([a-zA-Z_][a-zA-Z0-9_]*)|\$"
    Binop = r"\+|-|\*|\/|\^|\%|\.{2}|(<=)|<|(>=)|>|(==)|(!=)|(and)|(or)"
    Assign = r"=|(\*=)|(\%=)|(\^=)|(\+=)|(-=)|(/=)"
    Unop = r"-|(not)"
    SingleEqual = r"="
    Type = r"\b(number)|(string)|(list)|(bool)\b"
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
    Flag = "^--!"
    Comment = r"^//"
    Assign = "::="
    CurlyBrackets = r"(?<!\")\{(.*?)\}(?!\")"
    SquareBrackets = r"(?<!\")\[(.*?)\](?!\")"
    Rule = r"<\w*>"
    StringLiteral = r"[a-z0-9]*(\"(?:\\.|[^\\\"])*\"|\'(?:\\.|[^\\'])*\')"
    # Symbol = r"<([a-zA-Z_][a-zA-Z0-9_]*)>|<\$>"

    Pipe = r"\|"
    StatementSeperator = r"[\n]+"


class Keywords(Enum):
    NoRefresh = r"\b(norefresh)\b"
    Type = r"\b(number|string|list|bool)\b"
    Bool = r"\b(true)|(false)\b"
    BoolOp = r"(and)|(or)"
    Define = r"\b(define)\b"
    ElseIf = r"\b(elseif)\b"
    Return = r"\b(return)\b"
    Shared = r"\b(shared)\b"
    While = r"\b(while)\b"
    Break = r"\b(break)\b"
    Else = r"\b(else)\b"
    List = r"\b(list)\b"
    For = r"\b(for)\b"
    Var = r"\b(var)\b"
    Not = r"\b(not)\b"
    Let = r"\b(let)\b"
    If = r"\b(if)\b"
    In = r"\b(in)\b"


class CompilerRules(Enum):
    Flag = r"--!.*"
    Comment = r"//.*"

    StringLiteral = r"[a-z0-9]*(\"(?:\\.|[^\\\"])*\"|\'(?:\\.|[^\\'])*\')"

    NoRefresh = r"\b(norefresh)\b"
    Type = r"\b(number|string|list|bool)\b"
    Define = r"\b(define)\b"
    ElseIf = r"\b(elseif)\b"
    Return = r"\b(return)\b"
    Shared = r"\b(shared)\b"
    While = r"\b(while)\b"
    Break = r"\b(break)\b"
    Else = r"\b(else)\b"
    For = r"\b(for)\b"
    Var = r"\b(var)\b"
    Not = r"\b(not)\b"
    Let = r"\b(let)\b"
    If = r"\b(if)\b"
    In = r"\b(in)\b"

    Symbol = r"([a-zA-Z_][a-zA-Z0-9_]*)|\$"
    Number = r"[0-9][_0-9]*(\.[0-9][_0-9]*)?"

    # operators
    Multiply = r"\*="
    Modulate = r"\%="
    Exponate = r"\^="
    Add = r"\+="
    Subtract = "-="
    Divide = "/="
    # Binop = r"\+|-|\*|\/|\^|\%|\.{2}|(<=)|<|(>=)|>|(==)|(!=)|(and)|(or)"

    Equal = "=="
    NotEqual = "!="
    MoreOrEqual = ">="
    LessOrEqual = "<="
    MoreThan = ">"
    LessThan = "<"
    Assign = "="
    # # maths operators
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
    StatementSeperator = r"\n|;"


RuleType = BNFRules | CompilerRules | BNFPreDefined | Keywords
OptionalStr = str | None
Token = NamedTuple("Token", (("token_type", RuleType), ("token_str", str), ("location", tuple[int, int])))
Rule = NamedTuple("Rule", (("rule", str | Callable[[Token], bool]), ("optional", str)))
IncompleteRules = list[str, list[list[Rule]]] | list


@dataclass
class Variable:
    name: str
    type: str
    token: Token
    procedure_scope: str = None


class CompilerError(Exception):
    def __init__(self, error_type: str, lines: list[str], offending_token: Token, error_msg: str = "",
                 file: str = ""):
        super().__init__(error_msg)
        self.error_type: str = error_type
        self.lines: list[str] = lines
        self.offending_token: Token = offending_token
        self.error_msg: str = error_msg
        self.file: str = file

