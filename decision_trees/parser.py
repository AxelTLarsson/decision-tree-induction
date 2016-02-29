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
            ('STRING', r'(\w+[-]\w+)+'),            # A string, ok with '-'
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
            elif typ != 'SKIP':
                val = mo.group(typ)
                if typ == 'STRING' and val in keywords:
                    typ = val
                yield Lexer.Token(typ, val, line, mo.start() - line_start)
            pos = mo.end()
            mo = get_token(s, pos)
        if pos != len(s):
            raise RuntimeError('Unexpected character %r on line %d' %
                               (s[pos], line))


if __name__ == '__main__':
    test = '''
    @data
    4.4,?,1.5,?,Iris-setosa
    '''
    f = open('example.arff', 'r')
    test = f.read()
    for token in Lexer.tokenize(test):
        print(token)
