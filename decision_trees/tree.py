"""
Module containing decision tree induction.
"""

from collections import Counter


def decision_tree_learning(examples: list, attributes: list, parent_examples):
    """
    Decision tree learning algorithm as given in figure 18.5 in Artificial
    Intelligence A Modern Approach.

    :param examples: list of dictionaries containing examples to learn from
    :param attributes: list of all attributes in the examples
    :param parent_examples: list of all parent examples (can be the same as
        `examples` when first running)
    :return: DecisionTree, a decision tree
    """

    if not examples:
        return plurality_value(parent_examples)
    elif examples_have_same_classification(examples):
        return examples[0]["classification"]
    elif not attributes:
        return plurality_value(examples)
    else:
        imp = [importance(a, examples) for a in attributes]
        A = attributes[imp.index(max(imp))]  # essentially like argmax
        tree = DecisionTree(attr=A)
        for vk in get_attribute_values(A, examples):
            exs = [e for e in examples if e.get(A) == vk]
            att = [a for a in attributes if a != A]
            subtree = decision_tree_learning(exs, att, examples)
            tree.add_branch(vk=vk, subtree=subtree)

    return tree


def get_attribute_values(attr: str, examples: list):
    return set([e[attr] for e in examples])


def plurality_value(examples: list):
    """
    Returns the most common classification in a list of examples.

    :param examples: list of dictionaries with examples as entries, must
        contain the key "classification"
    :return: str, most common classification
    """
    return Counter([e["classification"] for e in examples]).most_common(1)[0][0]


def examples_have_same_classification(examples: list):
    if len(examples) == 1:
        return True
    else:
        for a in examples[1:]:
            if a["classification"] != examples[0]["classification"]:
                return False
    return True


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
    ex1 = {"Patrons": "None", "Hungry": "Yes", "classification": "No"}
    ex2 = {"Patrons": "Some", "Hungry": "Yes", "classification": "Yes"}
    ex3 = {"Patrons": "Full", "Hungry": "Yes", "classification": "Yes"}
    ex4 = {"Patrons": "Full", "Hungry": "No", "classification": "No"}

    # attributes = ["Patrons", "Hungry"]
    attributes = ["Hungry", "Patrons"]
    examples = [ex1, ex2, ex3, ex4]

    tree = decision_tree_learning(examples, attributes, examples)
    print(tree)



