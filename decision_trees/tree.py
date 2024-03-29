"""
Module containing decision tree induction.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from collections import Counter
from numpy import log2
from math import log
from scipy.stats import chisquare


# The confidence level to be used when pruning
CUTOFF = 0.05


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


def basic_importance(attr: str, examples: list):
    return 1


def B(q):
    """
    Binary entropy function for boolean values.
    q = 0.5 returns the maximum of 1
    q = 0 and q = 1 returns the minimum values of 0
    :param q: Boolean variable positive probability
    :return: entropy
    """
    if q == 0 or q == 1:
        return 0
    return -(q * log2(q) + (1 - q) * log2(1 - q))


def entropy_importance(attr: str, examples: list):
    p = len([1 for e in examples if e["classification"] == "Yes"])
    n = len([1 for e in examples if e["classification"] == "No"])

    remainder = 0
    for d in get_attribute_values(attr, examples):
        subset = [e for e in examples if e[attr] == d]
        pk = len([1 for e in subset if e["classification"] == "Yes"])
        nk = len([1 for e in subset if e["classification"] == "No"])
        remainder += (pk + nk) / (p + n) * B(pk / (pk + nk))

    return B(p / (p + n)) - remainder


def generalised_B(q, b):
    if q == 0 or q == 1:
        return 0
    return -q * log(q, b)


def generalised_entropy_importance(attr: str, examples: list, classes: list):
    outcomes = [
        len([1 for e in examples if e["classification"] == c])
        for c in classes
    ]
    total_entropy = sum([
        generalised_B(p / len(examples), b=len(classes))
        for p in outcomes
    ])

    remainder = 0
    for d in get_attribute_values(attr, examples):
        subset = [e for e in examples if e[attr] == d]

        outcomes_k = [
            len([1 for e in subset if e["classification"] == c])
            for c in classes
        ]

        remainder += sum([
            sum(outcomes_k) / sum(outcomes) *
            generalised_B(pk / sum(outcomes_k), b=len(classes))
            for pk in outcomes_k
        ])

    return total_entropy - remainder


def should_prune(attr, examples):
    """
    Decides if an attribute should be pruned. The decision is based on
    the p-value of the chi-squared distribution, if it is higher than
    CUTOFF then the branch should be pruned, otherwise not.
    :param attr: str of the attribute to potentially be pruned
    :param examples: the data
    :return: to prune or not to prune
    """
    p = len([1 for e in examples if e["classification"] == "Yes"])
    n = len([1 for e in examples if e["classification"] == "No"])
    obs = []
    exp = []
    delta = 0
    attrs = get_attribute_values(attr, examples)
    for d in attrs:
        subset = [e for e in examples if e[attr] == d]
        pk = len([1 for e in subset if e["classification"] == "Yes"])
        nk = len([1 for e in subset if e["classification"] == "No"])
        pk_hat = p * (pk + nk)/(p + n)
        nk_hat = n * (pk + nk)/(p + n)
        obs.append(pk)
        exp.append(pk_hat)
        obs.append(nk)
        exp.append(nk_hat)
        delta += ((pk - pk_hat)**2) / pk_hat + ((nk - nk_hat)**2) / nk_hat

    chi2, p = chisquare(obs, f_exp=exp, ddof=len(attrs) - 1)
    # print("should_prune {} Δ: {} \u03C7\u00B2: {}, p: {}".format(attr, delta, chi2, p))
    return p > CUTOFF


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


def decision_tree_learning(examples: list, attributes: list, parent_examples,
                           importance_function: callable):
    """
    Decision tree learning algorithm as given in figure 18.5 in Artificial
    Intelligence A Modern Approach.

    :param examples: list of dictionaries containing examples to learn from
    :param attributes: list of all attributes in the examples
    :param parent_examples: list of all parent examples (can be the same as
        `examples` when first running)
    :param importance_function: function that takes an attribute (str) and a
        list of examples and returns a number representing the importance of
        that attribute
    :return: DecisionTree, a decision tree
    """

    if not examples:
        return plurality_value(parent_examples)
    elif examples_have_same_classification(examples):
        return examples[0]["classification"]
    elif not attributes:
        return plurality_value(examples)
    else:
        imp = [importance_function(a, examples) for a in attributes]
        A = attributes[imp.index(max(imp))]  # essentially like argmax
        tree = DecisionTree(attr=A)
        for vk in get_attribute_values(A, examples):
            exs = [e for e in examples if e.get(A) == vk]
            att = [a for a in attributes if a != A]
            subtree = decision_tree_learning(exs, att, examples,
                                             importance_function)
            tree.add_branch(vk=vk, subtree=subtree)

    return tree



def multiclass_decision_tree_learning(examples: list, attributes: list,
                                      parent_examples: list, classes: list):
    """
    Decision tree learning algorithm as given in figure 18.5 in Artificial
    Intelligence A Modern Approach.

    :param examples: list of dictionaries containing examples to learn from
    :param attributes: list of all attributes in the examples
    :param parent_examples: list of all parent examples (can be the same as
        `examples` when first running)
    :param importance_function: function that takes an attribute (str) and a
        list of examples and returns a number representing the importance of
        that attribute
    :return: DecisionTree, a decision tree
    """

    if not examples:
        return plurality_value(parent_examples)
    elif examples_have_same_classification(examples):
        return examples[0]["classification"]
    elif not attributes:
        return plurality_value(examples)
    else:
        imp = [generalised_entropy_importance(a, examples, classes) for a in attributes]
        A = attributes[imp.index(max(imp))]  # essentially like argmax
        tree = DecisionTree(attr=A)
        for vk in get_attribute_values(A, examples):
            exs = [e for e in examples if e.get(A) == vk]
            att = [a for a in attributes if a != A]
            subtree = multiclass_decision_tree_learning(exs, att, examples, classes)
            tree.add_branch(vk=vk, subtree=subtree)

    return tree


def tree_performance(tree, data):
    correct = 0
    skipped = 0
    for e in data.examples:
        try:
            correct += tree.eval(e) == e["classification"]
        except ValueError:
            # found an example with an attribute value that hasn't been seen
            # by the tree
            skipped += 1
        except AttributeError:
            # tree likely built with all equal classifications, will naively
            # classify everything as one classification
            correct += tree == e["classification"]

    return correct / (len(data.examples))


def restaurant_learning_curve_plot():
    import matplotlib.pyplot as plt
    from decision_trees import parser
    from numpy.random import randint
    data = parser.parse("../data/restaurant.arff")

    attributes = list(data.attributes.keys())
    attributes = [a for a in attributes if a != "classification"]

    def get_bootstrap_dataset(data, n_examples):
        idx = randint(0, len(data.examples), n_examples)
        examples = [data.examples[i] for i in idx]
        attrs = set()
        for e in examples:
            attrs.intersection_update(e.keys())
        return parser.Data("subset", attrs, examples)

    navg = 20
    results = list()
    sizes = range(1, 101)
    for training_set_size in sizes:

        avg = 0
        for _ in range(navg):  # averaged across 20 trials
            train = get_bootstrap_dataset(data, n_examples=training_set_size)

            tree = decision_tree_learning(train.examples, attributes,
                                          train.examples, entropy_importance)
            avg += tree_performance(tree, data)

        results.append(avg / navg)

    plt.plot(list(sizes), results)
    plt.ylim(0.4, 1)
    plt.xlabel("Training set size")
    plt.ylabel("Correct test set classifications")
    plt.show()


def test_using_restaurant_example():
    from decision_trees import parser
    data = parser.parse("../data/restaurant.arff")

    attributes = list(data.attributes.keys())
    attributes = [a for a in attributes if a != "classification"]

    tree = decision_tree_learning(data.examples, attributes, data.examples,
                                  importance_function=entropy_importance)
    print(tree)
    print(tree_performance(tree, data))


def test_using_restaurant_example_multiclass():
    from decision_trees import parser
    data = parser.parse("../data/restaurant.arff")

    attributes = list(data.attributes.keys())
    attributes = [a for a in attributes if a != "classification"]

    tree = multiclass_decision_tree_learning(data.examples, attributes,
                                             data.examples, classes=["Yes", "No"])
    print(tree)
    print(tree_performance(tree, data))


def test_using_contact_lenses_example_multiclass():
    from decision_trees import parser
    data = parser.parse("../data/contact-lenses.arff")

    attributes = list(data.attributes.keys())
    classes = list(data.attributes.values())[-1]
    attributes = [a for a in attributes if a != "classification"]

    tree = multiclass_decision_tree_learning(data.examples, attributes,
                                             data.examples, classes)
    print(tree)
    print(tree_performance(tree, data))


def main():
    test_using_restaurant_example_multiclass()

if __name__ == '__main__':
    main()
