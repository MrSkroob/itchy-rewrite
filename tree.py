from __future__ import annotations
from rules import *


class TreeNode:
    new_children_layer = 0
    prev_layer = 0

    def  __init__(self, rule_name: str, text: str | None=None, parent: TreeNode | None=None):
        self.rule_name = rule_name
        self.text = text
        self.children: list[TreeNode] = []
        self.parent = parent
        self.layer = parent and (parent.layer + 1) or 0


    """
    FIXME 
    Gotta work out a way to append child nodes to the correct layer...
    """
    
    def append_ast(self, incomplete_rules: IncompleteRules, token: Token):
        if len(incomplete_rules) - 1 != TreeNode.prev_layer:
            if len(incomplete_rules) >= TreeNode.prev_layer:
                TreeNode.new_children_layer = TreeNode.prev_layer
            else:
                TreeNode.new_children_layer = len(incomplete_rules) - 1
            TreeNode.prev_layer = len(incomplete_rules) - 1

        start_node = self
        for layer, rule in enumerate(incomplete_rules):
            rule_name = rule[0]
            first_child = start_node.find_first_child(rule_name)
            if start_node.layer <= TreeNode.new_children_layer and first_child is not None:
                start_node = first_child
            # else:
            start_node = start_node.append_child(rule_name)
            start_node.append_child("RAW_STR", token.token_str)

    def get_parent(self):
        return self.parent

    def find_first_child(self, rule_name: str, text: str | None=None):
        for child in self.children:
            if child.rule_name == rule_name:
                return child
        return None
    
    def append_child(self, rule_name: str, text: str | None=None):
        node = TreeNode(rule_name, text, self)
        self.children.append(node)
        return node

    def __repr__(self):
        if self.text is not None:
            return str((self.rule_name, self.text))
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


def walk_tree(start_node: TreeNode):
    children = start_node.children
    print(start_node)
    for child in children:
        walk_tree(child)


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
