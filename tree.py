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

    So let's say we have something like this:

    var boolean
    var integer

    boolean = true
    integer = 0

    ideally the ast would look like this:

    <stat>
        <vardefstat> 
            var
            boolean
        <vardefstat>
            var
            integer
        <varassignstat>
            boolean
            <assignorcall>
                =
                true
        <varassignstat>
            integer
            <assignorcall>
                =
                0
    """
    def append_ast(self, incomplete_rules: IncompleteRules, token: Token):
        root_node = self
        if len(incomplete_rules) > 0:
            token_rule = incomplete_rules[-1][1:][0] # the rule generated after the token matched. 
            # print(token_rule)
            new_branch = False
        else:
            new_branch = True
        # print(new_branch)
        for rule in incomplete_rules:
            if not new_branch:
                child = root_node.find_first_child(rule[0])
                if child is not None:
                    root_node = child
                else:
                    root_node = root_node.append_child(rule[0])
            else:
                root_node = root_node.append_child(rule[0])
        root_node.append_child(token.token_str)

    def get_parent(self):
        return self.parent

    def find_first_child(self, rule_name: str, recursive: bool=False):
        if len(self.children) == 0:
            return None
        for child in self.children:
            if child.rule_name == rule_name:
                return child
            elif recursive:
                result = self.find_first_child(rule_name, recursive)
                if result is not None:
                    return result
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
