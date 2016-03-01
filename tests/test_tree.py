from unittest import TestCase
from decision_trees import tree


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

        t = tree.decision_tree_learning(examples, attributes, examples)

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

        t = tree.decision_tree_learning(examples, attributes, examples)

        ex1 = {"Patrons": "None", "Hungry": "Yes"}
        ex2 = {"Patrons": "Some", "Hungry": "Yes"}
        ex3 = {"Patrons": "Full", "Hungry": "Yes"}
        ex4 = {"Patrons": "Full", "Hungry": "No"}

        self.assertEqual(t.eval(ex1), "No")
        self.assertEqual(t.eval(ex2), "Yes")
        self.assertEqual(t.eval(ex3), "Yes")
        self.assertEqual(t.eval(ex4), "No")

