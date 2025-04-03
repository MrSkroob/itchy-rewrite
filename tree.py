from __future__ import annotations
from typing import Generator
from rules import *


class TreeNode:
    appended_tokens: set[Token] = set()

    def __init__(self, rule_name: str, node_id: int, token: Token | None = None, parent: TreeNode | None = None):
        self.rule_name = rule_name
        self.token = token
        self.id = node_id
        self.children: list[TreeNode] = []
        self.parent = parent
        self.layer = (parent and parent.layer + 1) or 0

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

    def find_first_child(self, node_id: int, recursive: bool = False):
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

    def append_child(self, rule_name: str, node_id: int, token: Token | None = None):
        node = TreeNode(rule_name, node_id, token, self)
        self.children.append(node)
        return node

    def __repr__(self):
        if self.token is not None:
            return self.token.token_str
        return self.rule_name

    def display_tree(self, indent: int = 0):
        print("\t" * indent + str(self))
        for child in self.children:
            child.display_tree(indent + 1)


def walk_tree(start_node: TreeNode) -> Generator[TreeNode]:
    children = start_node.children
    yield start_node
    for child in children:
        yield from walk_tree(child)


def walk_until_condition(node_generator: Generator[TreeNode], condition: Callable[[TreeNode], bool]):
    for node in node_generator:
        if condition(node):
            return node
    return None


def walk_until_token(node_generator: Generator[TreeNode]):
    return walk_until_condition(node_generator, lambda x: x.token is not None)


def walk_until_rule(node_generator: Generator[TreeNode], rule_name: str):
    return walk_until_condition(node_generator, lambda x: x.rule_name == rule_name)
