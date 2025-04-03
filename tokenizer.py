from __future__ import annotations
import re
import os
from tree import TreeNode, walk_tree, walk_until_rule, walk_until_token
from copy import deepcopy
from bnf_manipulation import de_string
# from pprint import pprint
from typing import Iterator
from rules import *


def within_span(spans: list[tuple[int, int]], span: tuple[int, int]) -> bool:
    """
    Returns if a given span is encompassed within a list of spans. 
    """
    for i in spans:
        lower_bound = i[0]
        upper_bound = i[1]
        if span[0] >= lower_bound and span[1] <= upper_bound:
            return True
    return False


class Tokenizer:
    def __init__(self, code: str, rules: RuleType):
        self.code = code
        self.rules = rules
        self.returned_tokens: list[Token] = []
        self.token_stream = self._tokens()

    def tokenise_line(self, line: str, line_number: int):
        matches: list[tuple[RuleType, str, tuple[int, int]]] = []
        spans = []
        for enum in self.rules:
            rule = enum.value
            match_objs: Iterator[re.Match[str]] = re.finditer(rule, line)
            for match_obj in match_objs:
                # I don't know why,
                # but group(0) is not included in .groups()?
                for i in range(len((match_obj.group(0),) + match_obj.groups())):
                    # if we've already matched this entire word before, skip.
                    if within_span(spans, match_obj.span(i)):
                        continue

                    if match_obj.group(i) is None:
                        continue

                    # appends the matches found, with the third index being the position we found it in.
                    matches.append((enum, match_obj.group(i), match_obj.span(i)))
                    spans.append(match_obj.span(i))

        # we sort the matches found by the position we find it in, so whenever we call
        # next() on this iterator, we'll get the next token in chronological order.
        matches.sort(key=lambda x: x[2][0])
        for match in matches:
            yield Token(match[0], match[1], (line_number, match[2][0]))

    # returns the next token from the token stream
    def get_next_token(self) -> Token | None:
        if len(self.returned_tokens) > 0:
            return self.returned_tokens.pop()
        else:
            try:
                return next(self.token_stream)
            except StopIteration:
                return None

    # compiler can give back the token once it's finished with it. 
    def return_token(self, token: Token):
        self.returned_tokens.insert(0, token)

    # returns a generator which gives you tokens
    def _tokens(self):
        seperator = re.compile(self.rules.StatementSeperator.value)
        for line_number, line in enumerate(re.split(seperator, self.code)):
            yield from self.tokenise_line(line, line_number)
            yield Token(self.rules.StatementSeperator, "\n", (line_number, 0))


# Each rule is grouped.
# If the rule was non-optional in the first place, it will always have a length of one. 
# If not, it will be grouped with the rest of its optional members. 

def comparator_factory(regex_str: str, inverted: bool = False):
    """Returns a function that compares a given token to the regex.
    Returns True on match. 
    """
    regex = re.compile(regex_str)

    def compare(token: Token):
        # In hindsight, I could simply compare the .token_type instead of using regex.
        match_obj = re.match(regex, token.token_str)
        return (match_obj is not None) and not inverted

    return compare


def match_groups(regex_strs: RuleType, inverted: bool = False):
    """Returns a function that compares a given token to multiple rules at once. 
    Returns True if all match. 
    """
    compiled: list[re.Pattern[str]] = []
    for i in regex_strs:
        compiled.append(re.compile(i.value))

    def compare(token: Token):
        for j in compiled:
            if re.match(j, token[1]) is not None:
                return not inverted
        return inverted

    return compare


def return_slice_or_empty(list_part):
    if len(list_part) > 0:
        return [list_part]
    else:
        return []


def _handle_rule_optionals(optional_str: str, optional_type: str):
    # The tokenizer consider optional rules as a singular rule.
    # As such, we create another tokenizer specifically for this inner section.

    # So we append into another list where the first rule will specify what type of optional it is.
    optionals = []
    for i in Tokenizer(optional_str, BNFRules).token_stream:
        token_type = i[0]
        token_str = i[1]
        if token_type is BNFRules.StringLiteral:
            optionals.append((comparator_factory(de_string(token_str)), optional_type))
            optional_type = "!"
        elif token_type is BNFRules.Rule:
            optionals.append((token_str, optional_type))
            optional_type = "!"
    return optionals


class BNFParser:
    def __init__(self, grammar: str):
        """
        Creates a parser for a given grammar.
        The parameter 'grammar' should be in EBNF/BNF. 
        """
        self.rules: dict[str, IncompleteRules] = {}
        self.literals: dict[str, Callable[[Token], bool]] = {}
        self.visited: set[tuple[str, Token]] = set()
        self.tokenizer = Tokenizer(grammar, BNFRules)

        # we compile some regex for building blocks.
        # these are for any rules in the bnf file that starts with a capital letter. 
        # such rules are made here because they can be represented easily with regex,
        # e.g. Numbers, Symbols, Booleans, etc.
        for existing_rule in BNFPreDefined:
            self._create_pre_defined_rule(existing_rule)

        for keyword in Keywords:
            self._create_pre_defined_rule(keyword)

    def _create_pre_defined_rule(self, rule: RuleType):
        if rule is BNFPreDefined.Symbol:
            rule_value = rule.value

            def compare_name(token: Token):
                return comparator_factory(rule_value)(token) and match_groups(Keywords, True)(
                    token)

            self.literals["<" + rule.name + ">"] = compare_name
        else:
            self.literals["<" + rule.name + ">"] = comparator_factory(rule.value)

    def _new_rule(self, name: str):
        token = self.tokenizer.get_next_token()
        if token is None:
            return

        token_type = token[0]
        token_str = token[1]

        if token_type is BNFRules.StatementSeperator:
            return

        if token_type is not BNFRules.Pipe:
            if token_type is BNFRules.StringLiteral:
                self.rules[name][-1].append([(comparator_factory(de_string(token_str)), "!")])
            elif token_type is BNFRules.CurlyBrackets:
                self.rules[name][-1].append(_handle_rule_optionals(token_str[1:-1], "*"))
            elif token_type is BNFRules.SquareBrackets:
                self.rules[name][-1].append(_handle_rule_optionals(token_str[1:-1], "?"))
            else:
                self.rules[name][-1].append([(token_str, "!")])
        elif len(self.rules[name][-1]) > 0:
            self.rules[name].append([])

        self._new_rule(name)

    def generate(self):
        """
        Converts the bnf file into a slightly more readable version for the compiler. 
        """
        while True:
            token = self.tokenizer.get_next_token()
            if token is None:
                break
            token_str = token[1]
            if token[0] is BNFRules.StatementSeperator:
                continue

            next_token = self.tokenizer.get_next_token()
            next_token_type = next_token[0]
            if next_token_type is BNFRules.Assign:
                self.rules[token_str] = [[]]
                self._new_rule(token_str.strip())
            else:
                self.tokenizer.return_token(next_token)


def _completed_rule(incomplete_rule: list[list[Rule]], incomplete_rules: IncompleteRules):
    if incomplete_rule[1][0][1] in ["!", "?"]:
        incomplete_rule[1].pop(0)
    elif incomplete_rule[1][0][1] == "*":
        incomplete_rule.insert(1, incomplete_rule[1][1:])

    if len(incomplete_rule[1]) == 0:
        incomplete_rules[-1].pop(1)


def _compute_to_append(rule: Rule, rule_tokens: list[Rule], option_sequence: list[list[Rule]], index: int) -> \
        list[list[Rule]]:
    """
    Compute the list of tokens to append based on the rule's option type.

    Option type meanings:
    - "!" : Mandatory rule (must match) - skip the current token and continue with the next.
    - "?" : Optional rule (1 or 0 occurrences) - skip one token and append the following tokens.
    - "*" : Repeating rule (0 or more occurrences) - append tokens starting at the current position.
    """
    if rule[1] != "!":
        if rule[1] == "?":
            return return_slice_or_empty(rule_tokens[1:]) + option_sequence[index + 1:]
        elif rule[1] == "*":
            return return_slice_or_empty(rule_tokens[1:]) + option_sequence[index:]
        else:
            raise SyntaxError(f"Unrecognised option type '{rule[1]}'")
    else:
        return return_slice_or_empty(rule_tokens[1:]) + option_sequence[index + 1:]


class Parser:
    def __init__(self, bnf_parser: BNFParser):
        self.rules: dict[str, IncompleteRules] = bnf_parser.rules
        self.literals: dict[str, Callable] = bnf_parser.literals
        self.visited: set[tuple[str, Token]] = set()

    def is_terminator(self, rule: Rule):
        if callable(rule[0]):
            return True
        elif rule[0] in self.literals:
            return True
        return False

    def _check_terminator(self, rule: Rule, token: Token):
        if callable(rule[0]):
            return rule[0](token)
        elif rule[0] in self.literals:
            return self.literals[rule[0]](token)
        return False

    def _append_incomplete_rule(
            self, token: Token, incomplete_rules: IncompleteRules, rule_name: str = "<stat>"
    ) -> int | bool:
        """
        Attempt to expand and append incomplete rules based on the given token and rule.
        
        Returns the length of the appended token sequence, or False if a loop is detected
        or no valid expansion exists.
        """
        # Prevent infinite recursion by checking if we've already visited this (rule_name, token) pair.
        if (rule_name, token) in self.visited:
            return False
        self.visited.add((rule_name, token))

        # Retrieve all possible option sequences for the current rule.
        rules = self.rules

        for option_sequence in rules[rule_name]:
            # Create a deep copy to avoid modifying the original option sequence.
            option_sequence = deepcopy(option_sequence)
            for index, rule_tokens in enumerate(option_sequence):
                # Use the first element of the rule_tokens as the current rule.
                rule = rule_tokens[0]
                if self.is_terminator(rule):
                    if self._check_terminator(rule, token):
                        # Terminator matched; compute the remainder of tokens to append.
                        to_append = _compute_to_append(rule, rule_tokens, option_sequence, index)
                        if to_append:
                            incomplete_rules.append([rule_name] + to_append)
                        return len(to_append)
                    elif rule[1] == "!":
                        # Mandatory terminator did not match; stop processing this option_sequence.
                        break
                else:
                    # Recursively try to expand a non-terminator rule.
                    nested_rules = []
                    result = self._append_incomplete_rule(token, nested_rules, rule[0])
                    if result is not False:
                        # If nested expansion produced tokens, combine them appropriately.
                        if nested_rules:
                            current_append = option_sequence[index:]
                        else:
                            current_append = _compute_to_append(rule, rule_tokens, option_sequence, index)
                        if current_append:
                            incomplete_rules.append([rule_name] + current_append)
                            if nested_rules:
                                incomplete_rules.extend(nested_rules)
                        return len(current_append)
                    if rule[1] == "!":
                        # Mandatory rule did not expand; break out.
                        break
        return False

    def _delete_finished_rules(self, incomplete_rules: IncompleteRules, delete_any: bool = False):
        if len(incomplete_rules) == 0:
            return

        rule_group: list[list[Rule]] = incomplete_rules[-1]

        if delete_any is True:
            if len(rule_group) > 1:
                if rule_group[1][0][1] != "!":
                    incomplete_rules[-1].pop()
                    return self._delete_finished_rules(incomplete_rules, delete_any)

        if len(rule_group) == 1:
            rule_name_popped = rule_group[0]

            incomplete_rules.pop()
            if len(incomplete_rules) == 0:
                return

            if incomplete_rules[-1][1][0][0] == rule_name_popped and (
                    incomplete_rules[-1][1][0][1] == "!" or delete_any):
                incomplete_rules[-1][1].pop(0)
                if len(incomplete_rules[-1][1]) == 0:
                    incomplete_rules[-1].pop(1)
                if len(incomplete_rules) == 0:
                    return
                if len(incomplete_rules[-1]) == 2 and incomplete_rules[-1][1][0][0] == rule_name_popped and (
                        incomplete_rules[-1][1][0][1] == "!" or delete_any):
                    incomplete_rules[-1][1].pop(0)
                    if len(incomplete_rules[-1][1]) == 0:
                        incomplete_rules[-1].pop(1)

            if len(incomplete_rules) == 0:
                return

            self._delete_finished_rules(incomplete_rules)

    def _handle_optional(self, rule: Rule, token: Token, unconsumed_rules: list[Rule | list[Rule]],
                         incomplete_rules: IncompleteRules, ast: TreeNode):
        if rule[1] == "!":
            return False

        if len(unconsumed_rules[1:]) == 0:
            if len(incomplete_rules) == 1:
                incomplete_rules.pop()
                result = self._append_incomplete_rule(token, incomplete_rules)
                ast.append_ast(incomplete_rules, token)
                return result

            ast.append_ast(incomplete_rules, token)

            incomplete_rules.pop()

            incomplete_rules[-1][1].pop(0)
            if len(incomplete_rules[-1][1]) == 0:
                incomplete_rules[-1].pop(1)
        else:
            ast.append_ast(incomplete_rules, token)
            incomplete_rules[-1].pop(1)

        self._delete_finished_rules(incomplete_rules)
        return self._pop_incomplete_rule(token, incomplete_rules, ast)

    def _pop_incomplete_rule(self, token: Token, incomplete_rules: IncompleteRules, ast: TreeNode) -> bool | int:
        if len(incomplete_rules) == 0:
            result = self._append_incomplete_rule(token, incomplete_rules)
            ast.append_ast(incomplete_rules, token)
            return result
        last_index = len(incomplete_rules) - 1
        incomplete_rule = incomplete_rules[last_index]

        unconsumed_rules = incomplete_rule[1:]

        if len(unconsumed_rules) == 0:
            incomplete_rules.pop()
            return True

        rule_tokens = unconsumed_rules[0]
        rule = rule_tokens[0]

        if self.is_terminator(rule):
            if not self._check_terminator(rule, token):
                return self._handle_optional(rule, token, unconsumed_rules, incomplete_rules, ast)
            else:
                ast.append_ast(incomplete_rules, token)
                _completed_rule(incomplete_rule, incomplete_rules)
                self._delete_finished_rules(incomplete_rules)
                return True
        else:
            rules_appended = self._append_incomplete_rule(token, incomplete_rules, rule[0])
            if rules_appended is not False:
                ast.append_ast(incomplete_rules, token)
                if rules_appended == 0:
                    _completed_rule(incomplete_rule, incomplete_rules)
                return True
            else:
                return self._handle_optional(rule, token, unconsumed_rules, incomplete_rules, ast)

    def parse(self, tokenizer: Tokenizer) -> TreeNode | tuple[Token, Rule]:
        incomplete_rules: IncompleteRules = []
        root_node = TreeNode("<prog>", 0)

        token = None

        for token in tokenizer.token_stream:
            match token[0]:
                case CompilerRules.Comment:
                    continue
                case CompilerRules.Flag:
                    continue
            self.visited.clear()
            if len(incomplete_rules) == 0:
                result = self._append_incomplete_rule(token, incomplete_rules)
                root_node.append_ast(incomplete_rules, token)
            else:
                result = self._pop_incomplete_rule(token, incomplete_rules, root_node)

            if not result and len(incomplete_rules) > 0:
                return token, incomplete_rules[-1][1][0]

        self._delete_finished_rules(incomplete_rules, True)
        if len(incomplete_rules) > 0:
            return token, incomplete_rules[-1][1][0]

        root_node.display_tree()

        return root_node


def var_in_scope(variable: Variable, procedure_stack: str):
    if variable.procedure_scope is None:
        return True
    return variable.procedure_scope == procedure_stack


class Compiler:
    def __init__(self, code_fname: str, grammar_fname: str):
        self.variables = {}
        self.temp_variables = {}
        self.procedures = {}
        self.current_procedure = ""

        with open(code_fname) as f:
            code = f.read()
            self.code_path = os.path.abspath(f.name)

        with open(grammar_fname) as f:
            grammar = f.read()

        bnf_parser = BNFParser(grammar)
        bnf_parser.generate()
        self.parser = Parser(bnf_parser)
        self.code = code
        self.lines = self.code.split("\n")
        self.tokenizer = Tokenizer(code, CompilerRules)

    def get_next_expected_rule(self, result: tuple[Token, Rule]):
        token_output = result[0][1]
        if result[0][0] is CompilerRules.StatementSeperator:
            token_output = "\\n"

        if not self.parser.is_terminator(result[1][0]):  # type: ignore
            next_rule = "' or '".join([i[0][0][0] for i in self.parser.rules[result[1][0]]])
        else:
            next_rule = result[1][0]

        error_msg = f"Expected '{next_rule}', got '{token_output}'"
        return error_msg

    def print_error(self, error: CompilerError):
        lines = error.lines
        token = error.offending_token
        line_number = token.location[0]

        print(f'  {error.error_type} in: "{self.code_path}" line {line_number + 1}')
        print("\t" + lines[line_number])
        print("\t" + " " * token.location[1] + "^HERE")
        print("  " + error.error_msg)

    def variable_in_scope(self, variable_name: str):
        if variable_name in self.variables:
            return True
        if variable_name in self.procedures:
            return True
        if variable_name in self.temp_variables:
            variable = self.temp_variables[variable_name]
            return variable.procedure_scope == self.current_procedure
        else:
            return False

    def generate_code(self, ast: TreeNode) -> list[CompilerError]:
        # blocks: dict[str] = {}
        warnings: list[CompilerError] = []
        self.variables: dict[str, Variable] = {}
        self.procedures: dict[str, tuple[Token, dict[str, str]]] = {}
        # no, these aren't really 'local variables'. They're only usable within a certain procedure.
        self.temp_variables: dict[str, Variable] = {}
        self.current_procedure = ""
        close_procedure = 0
        stack = []
        node_generator = walk_tree(ast)
        for node in node_generator:
            stack.append(node)

            if node.layer <= close_procedure:
                self.current_procedure = ""

            match node.rule_name:
                case "<vardefstat>":
                    var_type = next(node_generator).token.token_str
                    var_name = next(node_generator).token
                    if var_name.token_str in self.variables:
                        warning = CompilerError("Duplicate Declaration Warning",
                                                self.lines,
                                                var_name,
                                                f"You have already defined a variable with the same name on line "
                                                f"{self.variables[var_name.token_str].token.location[0] + 1}.")
                        warnings.append(warning)

                    self.variables[var_name.token_str] = Variable(var_name.token_str, var_type, var_name)
                case "<varassignstat>":
                    next(node_generator)
                    var_name = next(node_generator).token
                    # operator = next(node_generator).token
                    if not self.variable_in_scope(var_name.token_str):
                        raise CompilerError("Name Error",
                                              self.lines,
                                              var_name,
                                              f"Name '{var_name.token_str}' is not defined.",
                                              self.code_path)
                case "<function>":
                    function_name = next(node_generator).token

                    if self.current_procedure != "":
                        raise CompilerError("Scope Error",
                                              self.lines,
                                              function_name,
                                              f"Nested procedure definitions are invalid.",
                                              self.code_path)

                    args: dict[str, str] = {}

                    self.procedures[function_name.token_str] = (function_name, args)
                    if next(node_generator).rule_name == "<funcbody>":
                        if next(node_generator).rule_name == "<paramlist>":
                            while True:
                                arg_name = walk_until_token(node_generator).token
                                next(node_generator)
                                arg_type = next(node_generator).token.token_str
                                if arg_name.token_str in args:
                                    # raise error
                                    raise CompilerError("Name Error",
                                                          self.lines,
                                                          arg_name,
                                                          f"Duplicate '{arg_name.token_str}' argument.",
                                                          self.code_path)

                                args[arg_name.token_str] = arg_type
                                self.temp_variables[arg_name.token_str] = Variable(arg_name.token_str, arg_type,
                                                                                   arg_name, function_name.token_str)
                                if next(node_generator).rule_name == "<wrap>":
                                    self.current_procedure = function_name.token_str
                                    close_procedure = node.layer
                                    break

        return warnings

    def compile(self):
        result = self.parser.parse(self.tokenizer)
        if type(result) is not TreeNode:
            error_msg = self.get_next_expected_rule(result)
            error = CompilerError(
                "Syntax Error",
                self.lines,
                result[0],
                error_msg,
                self.code_path)

            self.print_error(error)
            return
        else:
            # pass
            try:
                warnings = self.generate_code(result)
                if len(warnings) > 0:
                    print("""
                The compiler encountered some potential issues.
                Your code will still run, but it's likely you will encounter unexpected behaviour.
                If you want these to halt compilation, add the '--!strict' flag at the top of your file.
                If you want to ignore these warnings, add the '--!nonstrict' flag at the top of your file.
                                          """)
                    for i in warnings:
                        self.print_error(i)
            except CompilerError as e:
                self.print_error(e)
