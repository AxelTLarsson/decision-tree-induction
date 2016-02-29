"""
Module containing decision tree induction.
"""


def decision_tree_learning(examples, attributes, parent_examples):
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
        tree = DecisionTree(test=A)
        for vk in A:
            exs = set()
            subtree = decision_tree_learning(exs, attributes - A, examples)
            tree.add_branch(A=vk, subtree=subtree)

    return tree


def plurality_value(examples):
    return 1


def examples_have_same_classification(examples: list):
    return [a != examples[0] for a in examples[1:]]


def importance(attr, examples):
    return 1


class DecisionTree:
    def __init__(self, test):
        self.test = test
        self.branches = dict()
        self.is_leaf_node = True
        self.value = "Value for {}".format(self.test)

    def add_branch(self, A, subtree):
        if isinstance(subtree, DecisionTree):
            self.is_leaf_node = False
            self.branches[A] = subtree
        else:
            self.value = subtree

    def exec_branch(self, vk):
        for attr, subtree in self.branches.items():
            if attr == vk:
                return subtree

    def eval(self, example: dict):
        # TODO: check that all required attributes (including those that occur
        # in all sub-branches) are found in the example

        # pass a dict excluding self.name {i:a[i] for i in a if i!=0}
        if example[self.name] == self.value:
            if self.is_leaf_node:
                return self.value
            else:
                for b in self.branches:
                    return b.eval(example)

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
        s = "{attr} = {val}{goal}\n".format(
            attr=self.name, val=self.test,
            goal=": " + self.value if self.is_leaf_node else ""
        )

        # TODO: recursively iterate this for each branch??
        for b in self.branches:
            s += "{attr} = {val}{goal}\n".format(
                attr=b.name, val=b.test,
                goal=": " + b.value if b.is_leaf_node else ""
            )
        return s


if __name__ == '__main__':
    # build an example tree
    example1 = {"Patrons": "None", "Hungry": "Yes"}
    example2 = {"Patrons": "Some", "Hungry": "Yes"}
    example3 = {"Patrons": "Full", "Hungry": "Yes"}
    example4 = {"Patrons": "Full", "Hungry": "No"}

    tree = DecisionTree(test="None")

    print(tree.value)



