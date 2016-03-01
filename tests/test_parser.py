from unittest import TestCase
from decision_trees.parser import Parser, Lexer


class TestParser(TestCase):

    def test_the_lexer(self):
        with open('data/contact-lenses.arff', 'r') as f:
            test = f.read()
            # since tokenize is a generator, we must convert to list
            # to be able to go through it more than once
            tokens = list(Lexer.tokenize(test))
            # for t in tokens:
            #    print(t)
            rels = filter(lambda t: t.typ == 'RELATION_DECL', tokens)
            self.assertEqual(1, len(list(rels)))
            attrs = filter(lambda t: t.typ == 'ATTR_DECL', tokens)
            self.assertEqual(5, len(list(attrs)))
            datas = filter(lambda t: t.typ == 'DATA_DECL', tokens)
            self.assertEqual(1, len(list(datas)))

    def test_contact_lenses_parsing(self):
        with open('data/contact-lenses.arff', 'r') as f:
            s = f.read()
            parser = Parser(Lexer.tokenize(s))
            data = parser.parse()

    def test_restaurant_lexing(self):
        with open('data/restaurant.arff', 'r') as f:
            s = f.read()
            tokens = list(Lexer.tokenize(s))
            rels = filter(lambda t: t.typ == 'RELATION_DECL', tokens)
            self.assertEqual(1, len(list(rels)))
            attrs = filter(lambda t: t.typ == 'ATTR_DECL', tokens)
            self.assertEqual(11, len(list(attrs)))
            datas = filter(lambda t: t.typ == 'DATA_DECL', tokens)
            self.assertEqual(1, len(list(datas)))

    def test_restaurant_parsin(self):
        # since the lexer returns a generator, we cannot
        # iterate through it more than once, thus cannot test
        # both lexing and parsing at the same time
        with open('data/restaurant.arff', 'r') as f:
            s = f.read()
            parser = Parser(Lexer.tokenize(s))
            data = parser.parse()

