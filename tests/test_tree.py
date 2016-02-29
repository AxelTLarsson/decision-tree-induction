from unittest import TestCase
from decision_trees.tree import DecisionTree


class TestDecisionTree(TestCase):
    def test_example_tree(self):
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

        self.assertEqual(tree.eval(example1), "No")
        self.assertEqual(tree.eval(example2), "Yes")
        self.assertEqual(tree.eval(example3), "Yes")
        self.assertEqual(tree.eval(example4), "No")

