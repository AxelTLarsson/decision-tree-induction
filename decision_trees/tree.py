"""
Module containing decision tree induction.
"""


def decision_tree_learning(examples, attributes, parent_attributes):

    if not examples:
        return plurality_value(parent_attributes)
    elif examples_have_same_classification(examples):
        return classification
    elif not attributes:
        return plurality_value(examples)
    else:
        A = max([importance(a, examples) for a in attributes])
        tree = new_decision_tree(root_test=A)
        for vk in A:
            exs = set()
            subtree = decision_tree_learning(exs, attributes - A, examples)
            tree.add_branch(A=vk, subtree=subtree)

    return tree


if __name__ == '__main__':
    pass




