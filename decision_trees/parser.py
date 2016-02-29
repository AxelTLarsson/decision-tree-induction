"""
The parser module for parsing the Weka ARFF format.
"""
import collections
import re


class Lexer:
    """
    The lexer (a.k.a scanner) is reponsible for tokenising the
    input string.
    At this moment it works by accepting a string with the contents
    to be tokenised the source file. In general this should probably
    not done that way. Instead lazily reading the file probably...
    """
    Token = collections.namedtuple('Token', ['typ', 'value', 'line', 'column'])

    def tokenize(s):
        keywords = {'IF', 'THEN', 'ENDIF', 'NEXT', 'GOSUB', 'RETURN'}
        token_specification = [
            ('COMMENT', r'%.*'),                    # One-line comment
            ('RELATION_DECL', r'@relation'),        # Relation declaration
            ('STRING', r'\w+(?:-?\w+)+'),            # A string, ok with '-'
            ('ATTR_DECL', r'@attribute'),           # Attribute declaration
            # Numeric datatypes; numeric, integer, real treated same
            ('NUM_DATATYPE', r'numeric|integer|real'),
            ('LEFT_CURLY', r'{'),                   # Match '{'
            ('RIGHT_CURLY', r'}'),                  # Match '}'
            ('SEMI', r','),                         # Match ','
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
    """

    def __init__(self, token_generator):
        self.token_generator = token_generator
        self.current_token = None

    def accept(self, token_type):
        if self.current_token.typ == token_type:
            # print("\nAccept {}".format(self.current_token))
            t = self.current_token
            self.next_token()
            return t
        else:
            raise RuntimeError(
                "Cannot acccept {}, current_token: {}".format(
                    token_type, self.current_token))

    def expect(self, token_type):
        if self.current_token is None:
            return False
        return self.current_token.typ == token_type

    def next_token(self):
        try:
            self.current_token = next(self.token_generator)
        except StopIteration:
            print('Parsing done')
            self.current_token = None

    def parse(self):
        # Init
        self.next_token()

        # Expecting @relation <string>
        self.accept("RELATION_DECL")
        rel = self.accept('STRING')
        print("Relation is {}".format(rel.value))

        # Expecting a number of @attribute <name> <datatype>
        # TODO should refactor to new method
        while self.expect('ATTR_DECL'):
            self.accept('ATTR_DECL')
            attr_name = self.accept('STRING')
            print("@attribute {}".format(attr_name.value))
            if self.expect('NUM_DATATYPE'):
                data_type = self.accept('NUM_DATATYPE')
                print("datatype is {}".format(data_type.value))
            elif self.expect('LEFT_CURLY'):
                self.accept('LEFT_CURLY')
                print(self.nominal_values())

        if self.expect('DATA_DECL'):
            self.data()
        else:
            raise RuntimeError('No DATA section found!')

    def nominal_values(self):
        """
        Parse nominal values, i.e. {nom1, nom2, nom3}
        Expecting that when this method called, curent_token
        is at nom1.
        """
        nominal_values = []
        nom1 = self.accept('STRING')
        nominal_values.append(nom1.value)
        while self.expect('SEMI'):
            self.accept('SEMI')
            nomx = self.accept('STRING')
            nominal_values.append(nomx.value)

        self.accept('RIGHT_CURLY')
        return nominal_values

    def data(self):
        """
        Parse the data section.
        """
        self.accept('DATA_DECL')

        # loop through the whole data section
        while self.expect('STRING'):

            datas = []
            data1 = self.accept('STRING')
            datas.append(data1.value)
            # one line
            while self.expect('SEMI'):
                self.accept('SEMI')
                data = self.accept('STRING')
                datas.append(data.value)
            print("Datas: {}".format(datas))


if __name__ == '__main__':
    pass
