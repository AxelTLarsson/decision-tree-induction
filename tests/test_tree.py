import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from unittest import TestCase
import unittest
from decision_trees import tree
from decision_trees import parser


class TestDecisionTree(TestCase):
    def test_example_tree(self):
        example1 = {"Patrons": "None", "Hungry": "Yes"}
        example2 = {"Patrons": "Some", "Hungry": "Yes"}
        example3 = {"Patrons": "Full", "Hungry": "Yes"}
        example4 = {"Patrons": "Full", "Hungry": "No"}

        # root tree
        root_tree = tree.DecisionTree(attr="Patrons")

        # sub branch
        sub1 = tree.DecisionTree(attr="Hungry")
        sub1.add_branch("Yes", "Yes")
        sub1.add_branch("No", "No")

        root_tree.add_branch("None", "No")
        root_tree.add_branch("Some", "Yes")
        root_tree.add_branch("Full", sub1)

        self.assertEqual(root_tree.eval(example1), "No")
        self.assertEqual(root_tree.eval(example2), "Yes")
        self.assertEqual(root_tree.eval(example3), "Yes")
        self.assertEqual(root_tree.eval(example4), "No")

    def test_examples_have_same_classification_function(self):
        ex1 = {"Patrons": "None", "Hungry": "Yes", "classification": "No"}
        ex2 = {"Patrons": "Some", "Hungry": "Yes", "classification": "Yes"}
        ex3 = {"Patrons": "Full", "Hungry": "Yes", "classification": "Yes"}
        ex4 = {"Patrons": "Full", "Hungry": "No", "classification": "No"}

        self.assertTrue(tree.examples_have_same_classification([ex3, ex2]))
        self.assertTrue(tree.examples_have_same_classification([ex1, ex4]))
        self.assertFalse(tree.examples_have_same_classification(
            [ex1, ex2, ex3]))

    def test_plurality_value_function(self):
        ex1 = {"Hungry": "Yes", "classification": "No"}
        ex2 = {"Hungry": "Yes", "classification": "Yes"}
        ex3 = {"Hungry": "Yes", "classification": "Yes"}
        ex4 = {"Hungry": "No", "classification": "No"}
        ex5 = {"Hungry": "No", "classification": "No"}
        ex6 = {"Hungry": "No", "classification": "No"}
        ex7 = {"Hungry": "No", "classification": "Yes"}

        l1 = [ex1, ex2, ex3, ex4, ex5, ex6, ex7]
        l2 = [ex1, ex2, ex3, ex7]
        self.assertEqual(tree.plurality_value(l1), "No")
        self.assertEqual(tree.plurality_value(l2), "Yes")

    def test_get_attribute_values(self):
        ex1 = {"Patrons": "None", "Hungry": "Yes", "classification": "No"}
        ex2 = {"Patrons": "Some", "Hungry": "Yes", "classification": "Yes"}
        ex3 = {"Patrons": "Full", "Hungry": "Yes", "classification": "Yes"}
        ex4 = {"Patrons": "Full", "Hungry": "No", "classification": "No"}

        examples = [ex1, ex2, ex3, ex4]

        self.assertEqual(tree.get_attribute_values("Patrons", examples),
                         {"None", "Some", "Full"})

        self.assertEqual(tree.get_attribute_values("Hungry", examples),
                         {"No", "Yes"})

    def test_decision_tree_learning_algorithm_order_1(self):
        ex1 = {"Patrons": "None", "Hungry": "Yes", "classification": "No"}
        ex2 = {"Patrons": "Some", "Hungry": "Yes", "classification": "Yes"}
        ex3 = {"Patrons": "Full", "Hungry": "Yes", "classification": "Yes"}
        ex4 = {"Patrons": "Full", "Hungry": "No", "classification": "No"}

        attributes = ["Patrons", "Hungry"]
        examples = [ex1, ex2, ex3, ex4]

        t = tree.decision_tree_learning(examples, attributes, examples,
                                        tree.basic_importance)

        ex1 = {"Patrons": "None", "Hungry": "Yes"}
        ex2 = {"Patrons": "Some", "Hungry": "Yes"}
        ex3 = {"Patrons": "Full", "Hungry": "Yes"}
        ex4 = {"Patrons": "Full", "Hungry": "No"}

        self.assertEqual(t.eval(ex1), "No")
        self.assertEqual(t.eval(ex2), "Yes")
        self.assertEqual(t.eval(ex3), "Yes")
        self.assertEqual(t.eval(ex4), "No")

    def test_decision_tree_learning_algorithm_order_2(self):
        ex1 = {"Patrons": "None", "Hungry": "Yes", "classification": "No"}
        ex2 = {"Patrons": "Some", "Hungry": "Yes", "classification": "Yes"}
        ex3 = {"Patrons": "Full", "Hungry": "Yes", "classification": "Yes"}
        ex4 = {"Patrons": "Full", "Hungry": "No", "classification": "No"}

        attributes = ["Hungry", "Patrons"]
        examples = [ex1, ex2, ex3, ex4]

        t = tree.decision_tree_learning(examples, attributes, examples,
                                        tree.basic_importance)

        ex1 = {"Patrons": "None", "Hungry": "Yes"}
        ex2 = {"Patrons": "Some", "Hungry": "Yes"}
        ex3 = {"Patrons": "Full", "Hungry": "Yes"}
        ex4 = {"Patrons": "Full", "Hungry": "No"}

        self.assertEqual(t.eval(ex1), "No")
        self.assertEqual(t.eval(ex2), "Yes")
        self.assertEqual(t.eval(ex3), "Yes")
        self.assertEqual(t.eval(ex4), "No")

    def test_binary_entropy_function(self):
        self.assertEqual(tree.B(0.5), 1)
        self.assertAlmostEqual(tree.B(0.99), 0.0807931358959)

    def test_entropy_importance_function_returns_equivalent_trees(self):

        ex1 = {"Patrons": "None", "Hungry": "Yes", "classification": "No"}
        ex2 = {"Patrons": "Some", "Hungry": "Yes", "classification": "Yes"}
        ex3 = {"Patrons": "Full", "Hungry": "Yes", "classification": "Yes"}
        ex4 = {"Patrons": "Full", "Hungry": "No", "classification": "No"}

        examples = [ex1, ex2, ex3, ex4]

        tree1 = tree.decision_tree_learning(
            examples,
            attributes=["Hungry", "Patrons"],
            parent_examples=examples,
            importance_function=tree.entropy_importance
        )

        tree2 = tree.decision_tree_learning(
            examples,
            attributes=["Patrons", "Hungry"],
            parent_examples=examples,
            importance_function=tree.entropy_importance
        )

        self.assertTrue(str(tree1) == str(tree2))

    def test_entropy_importance_on_book_example(self):
        data = parser.parse("data/restaurant.arff")

        self.assertAlmostEqual(
            tree.entropy_importance("Patrons", data.examples),
            0.540852082973
        )

        self.assertAlmostEqual(
            tree.entropy_importance("Type", data.examples),
            0
        )

        self.assertEqual(
            tree.entropy_importance("Alternate", data.examples),
            0
        )

    def test_generalised_entropy_importance_on_book_example(self):
        data = parser.parse("data/restaurant.arff")

        classes = ["Yes", "No"]

        self.assertAlmostEqual(
            tree.generalised_entropy_importance("Patrons", data.examples, classes),
            0.540852082973
        )

        self.assertAlmostEqual(
            tree.generalised_entropy_importance("Type", data.examples, classes),
            0
        )

        self.assertEqual(
            tree.generalised_entropy_importance("Alternate", data.examples, classes),
            0
        )

    def test_B(self):
        # loaded coin
        self.assertAlmostEqual(tree.B(0.99), 0.08, places=2)
        # fair coin
        self.assertEqual(tree.B(0.5), 1)

    def test_eval(self):
        data = parser.parse("data/restaurant.arff")
        attributes = list(data.attributes.keys())
        attrs = [a for a in attributes if a != "classification"]
        d_tree = tree.decision_tree_learning(
            data.examples, attrs,
            data.examples,
            importance_function=tree.entropy_importance)
        for example in data.examples:
            classification = example['classification']
            self.assertEqual(d_tree.eval(example), classification)

    def test_should_prune(self):
        data = parser.parse("data/restaurant.arff")
        attributes = list(data.attributes.keys())
        for a in [a for a in attributes if a != "classification"]:
            print(tree.should_prune(a, data.examples))


if __name__ == '__main__':
    unittest.main()
