"""
Module containing decision tree induction.
"""


def decision_tree_learning(examples: list, attributes: list, parent_examples):
    """
    Decision tree learning algorithm as given in figure 18.5 in Artificial
    Intelligence A Modern Approach.

    :param examples: XXX, examples containing attributes
    :param attributes: XXX, list of attributes
    :param parent_examples: XXX, list of parent examples
    :return: DecisionTree, a decision tree
    """

    if not examples:
        return plurality_value(parent_examples)
    elif examples_have_same_classification(examples):
        return examples[0].classification()
    elif not attributes:
        return plurality_value(examples)
    else:
        A = max([importance(a, examples) for a in attributes])
        tree = DecisionTree(attr=A)
        for vk in A:
            exs = [e for e in examples if e.get(A) == vk]
            att = [a for a in attributes if a != A]
            subtree = decision_tree_learning(exs, att, examples)
            tree.add_branch(vk=vk, subtree=subtree)

    return tree


def plurality_value(examples):
    return 1


def examples_have_same_classification(examples: list):
    return [a != examples[0] for a in examples[1:]]


def importance(attr, examples):
    return 1


class DecisionTree:
    def __init__(self, attr):
        self.attr = attr
        self.branches = dict()
        self.is_leaf_node = False
        self.value = None

    def add_branch(self, vk, subtree):
        if isinstance(subtree, DecisionTree):
            self.branches[vk] = subtree
        else:
            # Just add a dummy branch which is a leaf node and contains
            # the required value
            self.branches[vk] = DecisionTree(attr="Leaf")
            self.branches[vk].is_leaf_node = True
            self.branches[vk].value = subtree

    def eval(self, example: dict):
        # TODO: check that all required attributes (including those that occur
        # in all sub-branches) are found in the example
        tree = self
        while not tree.is_leaf_node:
            try:
                tree = tree.branches[example[tree.attr]]
            except KeyError:
                raise ValueError("Value '{}' not found among branches for "
                                 "{}".format(example[tree.attr], tree.attr))
        return tree.value

    def __str__(self):
        """
        Print the tree in an ascii format similar to the following:

            Attribute1 = value1
                Attribute2 = value1: No
                Attribute2 = value2: Yes
            Attribute1 = value2: No
            Attribute1 = value3
                Attribute3 = value1
                    Attribute4 = value1: No
                    Attribute4 = value2: Yes
                Attribute3 = value2: No
        """
        if self.is_leaf_node:
            return "Leaf node returns {}\n".format(self.value)
        s = ""
        tree = self
        for vk, subtree in tree.branches.items():
            s += "{attr} == {val}\n".format(attr=tree.attr, val=vk)
            s += "  " + "\n  ".join(str(subtree).split('\n'))[:-2]
        return s


if __name__ == '__main__':
    # build an example tree
    example1 = {"Patrons": "None", "Hungry": "Yes"}
    example2 = {"Patrons": "Some", "Hungry": "Yes"}
    example3 = {"Patrons": "Full", "Hungry": "Yes"}
    example4 = {"Patrons": "Full", "Hungry": "No"}

    # root tree
    tree = DecisionTree(attr="Patrons")

    # sub branch
    sub1 = DecisionTree(attr="Hungry")
    sub1.add_branch("Yes", "Yes")
    sub1.add_branch("No", "No")

    tree.add_branch("None", "No")
    tree.add_branch("Some", "Yes")
    tree.add_branch("Full", sub1)

    print(tree)

    print(tree.eval(example1))
    print(tree.eval(example2))
    print(tree.eval(example3))
    print(tree.eval(example4))


