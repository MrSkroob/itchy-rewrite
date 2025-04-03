from __future__ import annotations
from typing import Generator
from rules import *


class TreeNode:
    appended_tokens: set[Token] = set()
    def  __init__(self, rule_name: str, id: int, token: Token | None=None, parent: TreeNode | None=None):
        self.rule_name = rule_name
        self.token = token
        self.id = id
        self.children: list[TreeNode] = []
        self.parent = parent


    def append_ast(self, incomplete_rules: IncompleteRules, token: Token):
        match token.token_type:
            case CompilerRules.OpenCurlyBracket:
                return
            case CompilerRules.CloseCurlyBracket:
                return
            case CompilerRules.OpenSquareBracket:
                return
            case CompilerRules.CloseSquareBracket:
                return
            case CompilerRules.OpenBracket:
                return
            case CompilerRules.CloseBracket:
                return
            case CompilerRules.Comma:
                return
        if token in TreeNode.appended_tokens:
            return
        TreeNode.appended_tokens.add(token)
        if token.token_type is CompilerRules.StatementSeperator:
            return
        root_node = self
        for rule in incomplete_rules:
            rule_name = rule[0]
            rule_id = id(rule)
            root_node = root_node.find_first_child(rule_id) or root_node.append_child(rule_name, rule_id)
        root_node.append_child(token.token_str, 0, token)

    def find_first_child(self, node_id: int, recursive: bool=False):
        if node_id == 0:
            return None
        if len(self.children) == 0:
            return None
        for child in self.children:
            if child.id == node_id:
                return child
            elif recursive:
                result = self.find_first_child(node_id, recursive)
                if result is not None:
                    return result
        return None

    def append_child(self, rule_name: str, id: int, token: Token | None=None):
        node = TreeNode(rule_name, id, token, self)
        self.children.append(node)
        return node

    def __repr__(self):
        if self.token is not None:
            return self.token.token_str
        return self.rule_name
    
    def display_tree(self, indent: int=0):
        print("\t" * indent + str(self))
        for child in self.children:
            child.display_tree(indent + 1)

    
"""
[['<stat>', [('<assignorcall>', '!')]],
 ['<assignorcall>', [('<exp>', '!')]],
 ['<exp>', [('<equation>', '!')]],
 ['<equation>', [('<Binop>', '*'), ('<exp>', '!')]]]
"""


example_incomplete_rule = [
    ['<stat>', [('<assignorcall', '!')]],
    ['<assignorcall>', [('<exp>', '!')]],
    ['<exp>', [('<equation>', '!')]],
    ['<equation>', [('<Binop>', '*'), ('<exp>', '!')]]]

new_incomplete_rule = [
    ['<stat>', [('<assignorcall', '!')]],
    ['<assignorcall>', [('<exp>', '!')]],
    ['<exp>', [('<equation>', '!')]],
    ['<equation>', [('<Binop>', '*'), ('<exp>', '!')]]]

    
def append_ast(start_node: TreeNode, incomplete_rules: IncompleteRules):
    for layer, rule in enumerate(incomplete_rules):
        rule_name = rule[0]
        start_node = start_node.append_child(rule_name)
        # if start_node.rule_name == rule_name


def walk_tree(start_node: TreeNode, root_call: bool=True) -> Generator[TreeNode]:
    children = start_node.children
    yield start_node
    for child in children:
        yield from walk_tree(child, False)


def walk_until_condition(node_generator: Generator[TreeNode], condition: Callable[[TreeNode], bool]):
    for node in node_generator:
        if condition(node):
            return node
    return None


def walk_until_token(node_generator: Generator[TreeNode]):
    return walk_until_condition(node_generator, lambda x: x.token is not None)


def walk_until_rule(node_generator: Generator[TreeNode], rule_name: str):
    return walk_until_condition(node_generator, lambda x: x.rule_name == rule_name)


if __name__ == "__main__":
    """
    Test

    int n = 15
    # pointless program

    proc main():
        while n > 1:
            n = n / 2

    """ 
    root_node = TreeNode("<prog>")
    root_node.append_ast(example_incomplete_rule, Token(CompilerRules.Add, "+", (0, 0)))
    root_node.display_tree()
    # append_ast(root_node, example_incomplete_rule)
    # walk_tree(root_node)
    # root_node = TreeNode("PROG")
    # var_node = root_node.append_child("VAR")
    # proc_node = root_node.append_child("PROC")

    # var_node.append_child("INT", "int")
    # var_node.append_child("ID", "n")
    # var_node.append_child("NUM", "15")

    # proc_node.append_child("ID", "main")
    # proc_node.append_child("NOFORMAL")
    # while_node = proc_node.append_child("WHILE")

    # bool_node = while_node.append_child("GT")
    # assign_node = while_node.append_child("ASSN")

    # bool_node.append_child("ID", "n")
    # bool_node.append_child("NUM", "1")

    # assign_node.append_child("ID", "n")
    # div_node = assign_node.append_child("DIV")

    # div_node.append_child("ID", "n")
    # div_node.append_child("NUM", "2")

    # walk_tree(root_node)
