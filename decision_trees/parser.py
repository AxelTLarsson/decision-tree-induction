# -*- coding: utf-8 -*-
"""
The parser module for parsing the Weka ARFF format.
"""
import collections
import re


def parse(file):
    """
    Helper method to parse a file,
    returns a Data representation of the source file.
    """
    with open(file, 'r') as f:
        s = f.read()
        parser = Parser(Lexer.tokenize(s))
        return parser.parse()


class Lexer:
    """
    The lexer (a.k.a scanner) is reponsible for tokenising the
    input string.
    At this moment it works by accepting a string with the contents
    to be tokenised; the entire source file. In general this should probably
    not done that way. Instead lazily reading the file probably...
    However, the output is at lazy in the form of a generator
    """
    Token = collections.namedtuple('Token', ['typ', 'value', 'line', 'column'])

    def tokenize(s):
        """
        Returns a generator yielding tokens as long as any are available from
        the string s.
        """
        keywords = {'IF', 'THEN', 'ENDIF', 'NEXT', 'GOSUB', 'RETURN'}
        token_specification = [
            ('COMMENT', r'%.*'),                    # One-line comment
            ('RELATION_DECL', r'@relation'),        # Relation declaration
            # A string, ok with '-' and '–' as well as $, <, >, =, _ (\w)
            ('STRING', r'[\w$<>=]+(?:[-–]?[\w$<>=]+)*'),
            ('ATTR_DECL', r'@attribute'),           # Attribute declaration
            # Numeric datatypes; numeric, integer, real: treated same
            ('NUM_DATATYPE', r'numeric|integer|real'),
            ('LEFT_CURLY', r'{'),                   # Match '{'
            ('RIGHT_CURLY', r'}'),                  # Match '}'
            ('COMMA', r','),                         # Match ','
            # date and relational are left out of this impl for now

            ('DATA_DECL', r'@data'),                # Data declaration
            ('MISSING_DECL', r'\?'),                # For missing values

            ('NUMBER', r'\d+(?:\.?\d+)?'),          # Integer or decimal number
            ('NEWLINE', r'[\n]'),                   # Line endings
            ('SKIP', r'[ \t]'),                     # Skip over spaces and tabs
        ]
        tok_regex = '|'.join(
            '(?P<%s>%s)' % pair for pair in token_specification)
        get_token = re.compile(tok_regex, re.IGNORECASE).match
        line = 1
        pos = line_start = 0
        mo = get_token(s)
        while mo is not None:
            typ = mo.lastgroup
            if typ == 'NEWLINE':
                line_start = pos
                line += 1
            elif typ != 'SKIP' and typ != 'COMMENT':
                val = mo.group(typ)
                if typ == 'STRING' and val in keywords:
                    typ = val
                yield Lexer.Token(typ, val, line, mo.start() - line_start)
            pos = mo.end()
            mo = get_token(s, pos)
        if pos != len(s):
            raise RuntimeError('Unexpected character %r on line %d' %
                               (s[pos], line))


class Parser:
    """
    A simple recursive descent parser for a subset of Weka ARFF.
    Currently only nominal datatypes for the attributes are supported.
    """

    def __init__(self, token_generator):
        self.token_generator = token_generator
        self.current_token = None

    def accept(self, token_type):
        if self.current_token is None or self.current_token.typ != token_type:
            raise RuntimeError(
                "Cannot acccept {}, current_token: {}".format(
                    token_type, self.current_token))
        else:
            # print("\nAccept {}".format(self.current_token))
            t = self.current_token
            self.next_token()
            return t

    def expect(self, token_type):
        if self.current_token is None:
            return False
        return self.current_token.typ == token_type

    def next_token(self):
        try:
            self.current_token = next(self.token_generator)
        except StopIteration:
            self.current_token = None

    def parse(self):
        # Init
        self.next_token()

        # Expecting @relation <string>
        self.accept("RELATION_DECL")
        rel = self.accept('STRING').value

        # Expecting a number of @attribute <name> <datatype>
        self.attributes = self.attributes()

        # Expecting data section
        if self.expect('DATA_DECL'):
            data = self.data()
        else:
            raise RuntimeError('No DATA section found!')

        return Data(rel, self.attributes, data)

    def attributes(self):
        """
        Parse attribute decl lines, e.g. @attribute <name> <datatype>
        """
        dict = collections.OrderedDict()
        while self.expect('ATTR_DECL'):
            self.accept('ATTR_DECL')
            attr_name = self.accept('STRING')
            # print("@attribute {}".format(attr_name.value))
            if self.expect('NUM_DATATYPE'):
                data_type = self.accept('NUM_DATATYPE')
                # print("datatype is {}".format(data_type.value))
            elif self.expect('LEFT_CURLY'):
                self.accept('LEFT_CURLY')
                dict[attr_name.value] = self.nominal_values()
            else:
                raise RuntimeError('Not implemented', self.current_token)
        return dict

    def nominal_values(self):
        """
        Parse nominal values, i.e. {nom1, nom2, nom3}
        Expecting that when this method called, curent_token
        is at nom1.
        """
        nominal_values = []
        nom1 = self.accept('STRING')
        nominal_values.append(nom1.value)
        while self.expect('COMMA'):
            self.accept('COMMA')
            nomx = self.accept('STRING')
            nominal_values.append(nomx.value)

        self.accept('RIGHT_CURLY')
        return nominal_values

    def data(self):
        """
        Parse the data section. Return a list of OrderedDicts,
        one dict per example of the form 'attr1' : 'val1' etc.
        """
        self.accept('DATA_DECL')

        # loop through the whole data section
        examples = []   # list for all examples
        while self.expect('STRING'):

            # iterator for the attribute names
            attr_iter = iter(self.attributes)

            # ordered dictionary for one example
            example = collections.OrderedDict()
            data1 = self.accept('STRING')
            attr_name = next(attr_iter)
            example[attr_name] = data1.value
            # one line
            while self.expect('COMMA'):
                self.accept('COMMA')
                data = self.accept('STRING')
                attr_name = next(attr_iter)
                example[attr_name] = data.value

            examples.append(example)

        return examples


class Data:
    """
    The data structure for the parser to build.
    """

    def __init__(self, relation, attributes, data):
        self.relation = relation
        self.attributes = attributes
        # Expecting data to be a list of examples,
        # where each example is a dictionary of the
        # form { attribute1: val1, attribute2: val2,... }
        self.examples = data

    def __str__(self):
        def data_string():
            string = ""
            for ex in self.examples:
                string += str(ex) + "\n"
            return string

        return "Relation: {}\nAttributes: {}\nData:\n{}".format(
            str(self.relation),
            str(self.attributes),
            data_string())


if __name__ == '__main__':
    print("Running parser")
