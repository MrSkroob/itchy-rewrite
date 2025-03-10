from __future__ import annotations
import rules
from copy import deepcopy
from bnf_manipulation import de_string
from pprint import pprint
from typing import NamedTuple, Iterator, Any
import re


RuleType = rules.BNFRules | rules.CompilerRules | rules.BNFPreDefined


class Token(NamedTuple):
    token_type: RuleType
    token_str: str


class Rule(NamedTuple):
    rule: str | function
    optional: str


IncompleteRules = list[list[Rule | list[Rule]]]


def within_span(spans: list[list[int]], span: list[int]) -> bool:
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

    def tokenise_line(self, line: str):
        matches: list[tuple[RuleType, str, tuple[int, int]]] = []
        spans = []
        for enum in self.rules:
            rule = enum.value
            match_objs: Iterator[re.Match[str]] = re.finditer(rule, line)
            for match_obj in match_objs:
                match enum:
                    # if we match a comment or flag, we skip the entire line.
                    # comments can be simply ignored.
                    # flags are simple hard coded features that which we can use to 
                    # decide whether a function waits for screen refresh or not. 
                    case self.rules.Comment:
                        yield Token(self.rules.Comment, line[2:])
                        return 
                    case self.rules.Flag:
                        yield Token(self.rules.Flag, line[3:])
                        return
                    case _: # type: ignore

                        # i don't know why,
                        # but group(0) is not included in .groups()?
                        for i in range(len((match_obj.group(0),) + match_obj.groups())):
                            # if we've already matched this entire word before, skip.
                            if within_span(spans, match_obj.span(i)):
                                continue

                            if match_obj.group(i) is None:
                                continue
                            
                            # appends the matches found, with the third index being the position we found it in.
                            matches.append((enum, match_obj.group(i), match_obj.span(i)[0]))
                            spans.append(match_obj.span(i))

        # we sort the matches found by the position we find it in, so whenever we call
        # next() on this iterator, we'll get the next token in chronological order.
        matches.sort(key=lambda x: x[2])
        for match in matches:
            yield Token(match[0], match[1])

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
        for line in re.split(seperator, self.code.strip()):
            yield from self.tokenise_line(line)
            yield Token(self.rules.StatementSeperator, "\n")



# Each rule is grouped. 
# If the rule was non-optional in the first place, it will always have a length of one. 
# If not, it will be grouped with the rest of its optional members. 


def comparitor_factory(rule_name: str, regex_str: str, inverted: bool=False):
    regex = re.compile(regex_str)

    def compare(token: tuple[rules.BNFRules, str]):
        match_obj = re.match(regex, token[1])
        print("beep boop", rule_name, token[1], regex_str, (match_obj is not None) and not inverted)
        return (match_obj is not None) and not inverted    
    return compare


def match_groups(rule_name: str, regex_strs: list[rules.BNFPreDefined], inverted: bool=False):
    compiled: list[re.Pattern[str]] = []
    for i in regex_strs:
        compiled.append(re.compile(i.value))

    def compare(token: Token):
        for i in compiled:
            if re.match(i, token[1]) is not None:
                return not inverted
        return inverted
    
    return compare


def return_slice_or_empty(list_part):
    if len(list_part) > 0:
        return [list_part]
    else:
        return []


class Parser:
    def __init__(self, grammar: str):
        """
        Creates a parser for a given grammar.
        The parameter 'grammar' should be in EBNF/BNF. 
        """
        self.rules: dict[str, list[list[list[Rule]]]] = {}
        self.literals: dict[str, function] = {}
        self.visited: set[tuple[str, Token]] = set()
        self.tokenizer = Tokenizer(grammar, rules.BNFRules)     

        # we compile some regex for building blocks.
        # these are for any rules in the bnf file that starts with a capital letter. 
        # such rules are made here because they can be represented easily with regex,
        # e.g. Numbers, Symbols, Booleans, etc.
        for existing_rule in rules.BNFPreDefined:
            if existing_rule is rules.BNFPreDefined.Symbol:
                rule_name = existing_rule.name
                rule_value = existing_rule.value
                def compare_name(token: Token):
                    return comparitor_factory(rule_name, rule_value)(token) and match_groups(rule_name, rules.Keywords, True)(token)

                self.literals["<" + existing_rule.name + ">"] = compare_name
            else:
                self.literals["<" + existing_rule.name + ">"] = comparitor_factory(existing_rule.name, existing_rule.value)

    def handle_rule_optionals(self, optional_str: str, optional_type: str):
        # The tokenizer consider optional rules as a singular rule. 
        # As such, we create another tokenizer specifically for this inner section. 

        # So we append into another list where the first rule will specify what type of optional it is. 
        optionals = []
        for i in Tokenizer(optional_str, rules.BNFRules).token_stream:
            token_type = i[0]
            token_str = i[1]
            if token_type is rules.BNFRules.StringLiteral:                
                optionals.append((comparitor_factory(de_string(token_str), de_string(token_str)), optional_type))
                optional_type = "!"
            elif token_type is rules.BNFRules.Rule:
                optionals.append((token_str, optional_type))
                optional_type = "!"
        return optionals

    def new_rule(self, name: str):
        token = self.tokenizer.get_next_token()
        if token is None:
            return
        
        # generates a new rule based on the token retrieved. 
        
        token_type = token[0]
        token_str = token[1]

        if token_type is rules.BNFRules.StatementSeperator:
            return
        
        if not token_type is rules.BNFRules.Pipe:
            if token_type is rules.BNFRules.StringLiteral:
                self.rules[name][-1].append([(comparitor_factory(name, de_string(token_str)), "!")])
            elif token_type is rules.BNFRules.CurlyBrackets:
                self.rules[name][-1].append(self.handle_rule_optionals(token_str[1:-1], "*"))
            elif token_type is rules.BNFRules.SquareBrackets:
                self.rules[name][-1].append(self.handle_rule_optionals(token_str[1:-1], "?"))
            else:
                self.rules[name][-1].append([(token_str, "!")])
        elif len(self.rules[name][-1]) > 0:
            self.rules[name].append([])
            
        self.new_rule(name)

    def generate(self):
        """
        Converts the bnf file into a slightly more readable version for the compiler. 
        """
        while True:
            token = self.tokenizer.get_next_token()
            if token is None:
                break
            token_str = token[1]    
            if token[0] is rules.BNFRules.StatementSeperator:
                continue

            next_token = self.tokenizer.get_next_token()
            next_token_type = next_token[0]
            if next_token_type is rules.BNFRules.Assign:
                self.rules[token_str] = [[]]
                self.new_rule(token_str.strip())
            else:
                self.tokenizer.return_token(next_token)

    def _is_terminator(self, rule: Rule):
        """Checks if a given rule is a terminator or not."""
        if callable(rule[0]):
            return True
        elif rule[0] in self.literals:
            return True
        return False

    def _check_terminator(self, rule: Rule, token: tuple[rules.BNFPreDefined, str]):
        """Checks if a given rule is a terminator or not, and returning the match result."""
        if callable(rule[0]):
            return rule[0](token)
        elif rule[0] in self.literals:
            print("excuse me what the actual fuck?", self.literals[rule[0]](token))
            return self.literals[rule[0]](token)
        return False

    def _append_incomplete_rule(self, token: Token, incomplete_rules: IncompleteRules, rule_name: str="<chunk>") -> int | bool:
        if (rule_name, token) in self.visited:
            return False
        self.visited.add((rule_name, token))
        rules = self.rules
        for options in rules[rule_name]:
            optional_offset = 0
            # EWWWWW
            options = deepcopy(options)
            for rule_tokens in options:
                rule = rule_tokens[0]
                pprint(options)
                print("trying out", rule)
                if self._is_terminator(rule):
                    if self._check_terminator(rule, token):
                        if rule[1] != "!":
                            if rule[1] == "?":
                                print("Question", rule_tokens)
                                to_append = return_slice_or_empty(rule_tokens[1:]) + options[optional_offset + 1:]
                            elif rule[1] == "*":
                                print("star", rule_tokens, options[optional_offset:])
                                print([rule_tokens[1:]] + options[optional_offset:])
                                to_append = return_slice_or_empty(rule_tokens[1:]) + options[optional_offset:]
                            else:
                                raise SyntaxError(f"Unrecognised option type '{rule[1]}'")
                        else:
                            to_append = return_slice_or_empty(rule_tokens[1:]) + options[optional_offset + 1:]

                        if len(to_append) > 0:
                            incomplete_rules.append([rule_name] + to_append)
                        # print(rule, "matched")
                        print("what the actual fuck?")
                        return len(to_append)
                    elif rule[1] == "!":
                        print("?!")
                        break
                else:
                    to_append = []
                    print("Stepping into", rule[0])
                    rules_appended = self._append_incomplete_rule(token, to_append, rule[0])
                    if rules_appended is not False:
                        print("Stepping out and matched", rule[0], "returned to", rule_name)
                        if len(to_append) > 0:
                            print("Child rule unfinished, appending entire parent rule")
                            current_append = options[optional_offset:]
                        else:
                            print("Child rule finished, appending rest of parent rule")
                            if rule[1] != "!":
                                if rule[1] == "?":
                                    current_append = return_slice_or_empty(rule_tokens[1:]) + options[optional_offset + 1:]
                                elif rule[1] == "*":
                                    current_append = return_slice_or_empty(rule_tokens[1:]) + options[optional_offset:]
                                else:
                                    raise SyntaxError(f"Unrecognised option type '{rule[1]}'")
                            else:
                                current_append = return_slice_or_empty(rule_tokens[1:]) + options[optional_offset + 1:]

                        if len(current_append) > 0:
                            incomplete_rules.append([rule_name] + current_append)
                            if len(to_append) > 0:
                                print("Appending child rule")                          
                                for i in to_append:
                                    incomplete_rules.append(i)

                        return len(current_append)
                    print("Stepping out", rule[0])
                    if rule[1] == "!":
                        break
                optional_offset += 1
                print(rule, "was an optional. Try next one.")
        
        print("No match for", rule_name)
        return False
    
    def _delete_finished_rules(self, incomplete_rules: IncompleteRules):
        rule_group = incomplete_rules[-1]

        if len(rule_group) == 1:
            print("Rule finished completely, popping all parents.")
            rule_name_popped = rule_group[0]
            incomplete_rules.pop()

            print("Popping", rule_name_popped)

            if len(incomplete_rules) == 0:
                return

            if incomplete_rules[-1][1][0][0] == rule_name_popped and incomplete_rules[-1][1][0][1] == "!":
                incomplete_rules[-1][1].pop(0)
                if len(incomplete_rules[-1][1]) == 0:
                    incomplete_rules[-1].pop(1)
                if len(incomplete_rules) == 0:
                    return
                if len(incomplete_rules[-1]) == 2 and incomplete_rules[-1][1][0][0] == rule_name_popped and incomplete_rules[-1][1][0][1] == "!":
                    incomplete_rules[-1][1].pop(0)
                    if len(incomplete_rules[-1][1]) == 0:
                        incomplete_rules[-1].pop(1)
            
            if len(incomplete_rules) == 0:
                return
                
            self._delete_finished_rules(incomplete_rules)

    def _handle_optional(self, rule: str, token: Token, unconsumed_rules: list[Rule | list[Rule]], incomplete_rules: IncompleteRules):
        if rule[1] == "!":
            return False
        print("Was optional, go next.")
        if len(unconsumed_rules[1:]) == 0:
            print("Optional skipped completely.")
            incomplete_rules.pop()
            
            if len(incomplete_rules) == 0:
                return self._append_incomplete_rule(token, incomplete_rules)

            print(incomplete_rules[-1][1])
            incomplete_rules[-1][1].pop(0)
            if len(incomplete_rules[-1][1]) == 0:
                incomplete_rules[-1].pop(1)
            
            pprint(incomplete_rules)
        else:
            incomplete_rules[-1].pop(1)
        self._delete_finished_rules(incomplete_rules)
        return self._pop_incomplete_rule(token, incomplete_rules)
        

    def _pop_incomplete_rule(self, token: Token, incomplete_rules: IncompleteRules):
        if len(incomplete_rules) == 0:
            return self._append_incomplete_rule(token, incomplete_rules)
        last_index = len(incomplete_rules) - 1
        incomplete_rule = incomplete_rules[last_index]
        # rule_name = incomplete_rule[0]

        unconsumed_rules = incomplete_rule[1:]

        if len(unconsumed_rules) == 0:
            return False

        rule_tokens = unconsumed_rules[0]
        rule = rule_tokens[0]

        print("trying out", rule)

        if self._is_terminator(rule):
            print("Matching existing", rule)
            if not self._check_terminator(rule, token):
                return self._handle_optional(rule, token, unconsumed_rules, incomplete_rules)
            else:
                print("Matched!", incomplete_rule)
                if incomplete_rule[1][0][1] in ["!", "?"]:
                    incomplete_rule[1].pop(0)
                elif incomplete_rule[1][0][1] == "*":
                    incomplete_rule.insert(1, incomplete_rule[1][1:])
                if len(incomplete_rule[1]) == 0:
                    incomplete_rules[-1].pop(1)
                self._delete_finished_rules(incomplete_rules)
                return True
        else:
            print("Appending to rules...")
            rules_appended = self._append_incomplete_rule(token, incomplete_rules, rule[0])
            if rules_appended is not False:
                print("Added rules")
                print(rules_appended)
                return True
            else:
                return self._handle_optional(rule, token, unconsumed_rules, incomplete_rules)


    def parse(self, tokenizer: Tokenizer):
        incomplete_rules: IncompleteRules = []

        line_number = 0

        for token in tokenizer.token_stream:
            if token[0] is rules.CompilerRules.Comment:
                continue
            elif token[0] is rules.CompilerRules.Flag:
                continue
            elif token[0] is rules.CompilerRules.StatementSeperator:
                line_number += 1
                continue

            self.visited.clear()
            print("===[New check]===")
            print(token)
            if len(incomplete_rules) == 0:
                print("Appending to rules...")
                result = self._append_incomplete_rule(token, incomplete_rules)
            else:
                print("Popping rules...")
                result = self._pop_incomplete_rule(token, incomplete_rules)
            if not result and len(incomplete_rules) > 0:
                print("===[Syntax error]===")
                pprint(incomplete_rules)
                raise SyntaxError(f"D: line {line_number}")
            
            print("Success! These are the remaining rules:")
            pprint(incomplete_rules)

        
        if len(incomplete_rules) > 0 and self._pop_incomplete_rule(Token(rules.BNFRules.StatementSeperator, "\n"), incomplete_rules):
            raise SyntaxError(f"D: Expected something, but got EOF.")

        print("Compiled with no issues.")


def generate_code():
    pass